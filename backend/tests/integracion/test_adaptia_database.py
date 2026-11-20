import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Event
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.base_datos.session import get_engine
from app.configuracion.settings import Settings, get_settings
from app.main import create_app
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.integracion_adaptia.errors import IntegrationError, RequestContext
from app.modulos.integracion_adaptia.models import AdaptiaGeneration
from app.modulos.integracion_adaptia.repository import AdaptiaRepository
from app.modulos.integracion_adaptia.router import EXAMPLE
from app.modulos.integracion_adaptia.schemas import AdaptiaGenerationRequest
from app.modulos.integracion_adaptia.service import AdaptiaService
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationResult, TokenUsage
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.usuarios.models import User
from tests.fixtures.content_reference import request as content_request
from tests.fixtures.content_reference import retrieval

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Requiere PostgreSQL aislado y migraciones"
    ),
]
TOKEN = "synthetic-integration-token-for-tests-only"


def settings():
    return Settings(
        _env_file=None,
        adaptia_enabled=True,
        adaptia_service_token=TOKEN,
        llm_enabled=True,
        llm_free_tier_confirmed=True,
        llm_default_provider="gemini",
        llm_model="integration-test",
    )


def result():
    return GenerationResult(
        provider="gemini",
        requested_model="integration-test",
        latency_ms=5,
        usage=TokenUsage(total_tokens=120),
        text=json.dumps(
            {
                "title": "Derivadas",
                "sections": [
                    {"type": "explanation", "title": "Idea", "text": "La derivada mide el cambio."},
                    {"type": "example", "title": "Ejemplo", "text": "La derivada de x² es 2x."},
                    {"type": "exercise", "title": "Practica", "text": "Deriva x³."},
                ],
            }
        ),
    )


@pytest.fixture
def database():
    engine = get_engine()
    # Estas pruebas de concurrencia confirman commits reales y limpian solo la BD aislada.
    assert engine.url.database == "adaptia_tests"
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE generaciones_adaptia, generaciones_contenido CASCADE"))
    yield engine
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE generaciones_adaptia, generaciones_contenido CASCADE"))


@pytest.fixture
def provider(monkeypatch):
    provider = Mock()
    provider.generate.return_value = result()
    monkeypatch.setattr(
        "app.modulos.integracion_adaptia.service.create_provider", lambda _: provider
    )
    return provider


def call(engine, request_id, payload=None, session="session_integration"):
    with Session(engine, expire_on_commit=False) as db:
        return AdaptiaService(AdaptiaRepository(db), settings()).generate(
            AdaptiaGenerationRequest(**(payload or EXAMPLE)), RequestContext(request_id, session)
        )


@pytest.mark.parametrize(
    "usage,expected_total",
    [
        (TokenUsage(total_tokens=120), 120),
        (TokenUsage(input_tokens=30, output_tokens=20, reasoning_tokens=7), None),
    ],
)
def test_real_http_contract_persistence_and_success_replay(
    database, provider, usage, expected_total
):
    provider.generate.return_value = result().model_copy(update={"usage": usage})
    app = create_app()
    app.dependency_overrides[get_settings] = settings
    with TestClient(app) as browser:
        headers = {"Authorization": "Bearer " + TOKEN, "X-Request-ID": "workflow_integration"}
        first = browser.post("/api/v1/tutoria/generate-content", json=EXAMPLE, headers=headers)
        assert first.status_code == 200, first.text
        body = first.json()
        assert body["data"]["metadata_generation"]["tokens_used"] == expected_total
        assert body["success"] is True and body["tracking"]["request_id"] == "workflow_integration"
        assert body["data"]["content"] and len(body["data"]["structure"]["sections"]) == 3
        repeated = browser.post("/api/v1/tutoria/generate-content", json=EXAMPLE, headers=headers)
        assert repeated.status_code == 200 and repeated.json()["metadata"]["replayed"] is True
        assert repeated.json()["data"] == body["data"]
    provider.generate.assert_called_once()
    with Session(database) as db:
        row = db.get(AdaptiaGeneration, "workflow_integration")
        assert row.status == "succeeded" and row.completed_at is not None
        assert row.student_id_hash == EXAMPLE["student_id"]
        assert row.request_snapshot["difficulty"] == 5
        assert row.usage == usage.model_dump()
        assert row.response["data"] == body["data"]
        assert len(row.payload_sha256) == len(row.prompt_sha256) == 64


@pytest.mark.parametrize("second_id,status", [("request_concurrent", 409), ("request_other", 429)])
def test_concurrent_requests_cause_one_provider_call(database, provider, second_id, status):
    entered, proceed = Event(), Event()

    def generate(_):
        entered.set()
        assert proceed.wait(10)
        return result()

    provider.generate.side_effect = generate
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(call, database, "request_concurrent")
        assert entered.wait(10)
        try:
            with pytest.raises(IntegrationError) as error:
                call(database, second_id)
            assert error.value.status == status
        finally:
            proceed.set()
        assert first.result(timeout=15).success is True
    assert call(database, "request_concurrent").metadata.replayed is True
    provider.generate.assert_called_once()
    with Session(database) as db:
        assert db.scalar(select(func.count()).select_from(AdaptiaGeneration)) == 1


def test_same_id_different_payload_is_conflict_even_after_success(database, provider):
    call(database, "request_conflict")
    with pytest.raises(IntegrationError) as error:
        call(database, "request_conflict", {**EXAMPLE, "difficulty": 9})
    assert error.value.status == 409
    provider.generate.assert_called_once()


def test_failure_is_persisted_and_same_id_never_sends_again(database, provider):
    provider.generate.side_effect = ProviderError("llm_timeout")
    with pytest.raises(IntegrationError) as first:
        call(database, "request_timeout")
    assert first.value.status == 503
    with pytest.raises(IntegrationError) as second:
        call(database, "request_timeout")
    assert second.value.status == 409
    provider.generate.assert_called_once()
    with Session(database) as db:
        row = db.get(AdaptiaGeneration, "request_timeout")
        assert row.status == "failed" and row.error_code == "llm_timeout"
        assert row.completed_at is not None and row.response is None


def test_api_usage_is_visible_in_existing_web_quota(database, provider):
    call(database, "request_web_quota")
    with Session(database) as db:
        used, resets_at = GenerationClaimRepository(db).daily_usage()
        assert used == 1 and resets_at > datetime.now(UTC)
    with pytest.raises(IntegrationError) as error:
        call(database, "request_rate_limited")
    assert error.value.status == 429
    provider.generate.assert_called_once()


def test_shared_daily_limit_counts_failures(database, provider):
    provider.generate.side_effect = ProviderError("llm_timeout")
    with pytest.raises(IntegrationError):
        call(database, "request_day_one")
    with Session(database) as db:
        db.execute(
            update(AdaptiaGeneration).values(
                generation_started_at=func.clock_timestamp() - text("INTERVAL '2 minutes'")
            )
        )
        db.commit()
        configured = settings().model_copy(update={"llm_daily_request_limit": 1})
        with pytest.raises(IntegrationError) as error:
            AdaptiaService(AdaptiaRepository(db), configured).generate(
                AdaptiaGenerationRequest(**EXAMPLE), RequestContext("request_daily_blocked", "s")
            )
        assert error.value.status == 429
    provider.generate.assert_called_once()


def test_reservation_is_committed_before_external_provider(database, provider):
    def generate(_):
        with Session(database) as other:
            row = other.get(AdaptiaGeneration, "request_durable")
            assert row.status == "generating" and row.response is None
        return result()

    provider.generate.side_effect = generate
    assert call(database, "request_durable").success is True


@pytest.mark.parametrize("state,age,daily_limit", [("failed", 120, 1), ("generating", 0, 5)])
def test_web_usage_and_busy_state_limit_the_integration(
    database, provider, state, age, daily_limit
):
    with Session(database, expire_on_commit=False) as db:
        owner = User(
            institutional_email=f"adaptia-{uuid4().hex}@example.org",
            nombre="Docente",
            apellido="Sintético",
            rol="teacher",
            last_login=datetime.now(UTC),
        )
        db.add(owner)
        db.commit()
        identifier = GenerationRepository(db).prepare(
            owner.id, EducationalPromptBuilder().build(content_request(), retrieval())
        )
        row = db.get(ContentGeneration, identifier)
        row.status = state
        row.generation_started_at = datetime.now(UTC) - timedelta(seconds=age)
        if state == "failed":
            row.completed_at = datetime.now(UTC)
            row.error_code = "llm_timeout"
        db.commit()
        configured = settings().model_copy(update={"llm_daily_request_limit": daily_limit})
        with pytest.raises(IntegrationError) as error:
            AdaptiaService(AdaptiaRepository(db), configured).generate(
                AdaptiaGenerationRequest(**EXAMPLE), RequestContext("blocked_by_web", "session")
            )
        assert error.value.status == 429
        provider.generate.assert_not_called()
