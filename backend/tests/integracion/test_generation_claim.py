from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import update

from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.execution_schemas import ExecutionConfiguration
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.contenidos.repositorios.history_repository import HistoryRepository
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.history_service import HistoryService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.documentos.models import Document
from app.modulos.proveedores_ia.schemas import GenerationTarget
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.rag.servicios.model_spec import (
    DIMENSIONS,
    EMBEDDING_VERSION,
    MODEL_ID,
    MODEL_REVISION,
)
from tests.fixtures.content_reference import request, retrieval
from tests.integracion.test_content_trace_database import pytestmark as trace_marks
from tests.integracion.test_content_trace_database import response
from tests.integracion.test_content_trace_database import trace_database as trace_database

pytestmark = trace_marks
TARGET = GenerationTarget(provider="gemini", requested_model="model-test-v1")


@pytest.fixture
def claim_database(trace_database):
    db, _, _ = trace_database
    # Solo dentro del savepoint reversible del fixture, nunca borra datos reales.
    db.execute(update(ContentGeneration).values(generation_started_at=None))
    db.commit()
    return trace_database


def published_source(db, owner):
    found = retrieval()
    hit = found.results[0]
    hit.course = "cálculo diferencial"
    hit.version_number = 1
    hit.source_reference = "Material sintético"
    hit.published_at = datetime.now(UTC)
    db.add(
        Document(
            id=hit.document_id,
            owner_id=owner,
            filename=hit.filename,
            title=hit.document_title,
            mime_type="text/plain",
            size_bytes=10,
            sha256=hit.document_sha256,
            course=hit.course,
            source_reference=hit.source_reference,
            permission_note="Permiso sintético",
            permission_recorded_at=datetime.now(UTC),
            published_at=hit.published_at,
            processing_status="processed",
            processing_version=hit.processing_version,
            index_status="indexed",
            chunk_count=1,
            embedding_model=MODEL_ID,
            embedding_revision=MODEL_REVISION,
            embedding_version=EMBEDDING_VERSION,
        )
    )
    db.flush()
    db.add(
        DocumentChunk(
            id=hit.id,
            document_id=hit.document_id,
            position=hit.position,
            source_kind=hit.source_kind,
            source_index=hit.source_index,
            char_start=hit.char_start,
            char_end=hit.char_end,
            text=hit.text,
            source_sha256=hit.source_sha256,
            embedding=[1.0] + [0.0] * (DIMENSIONS - 1),
            embedding_tokens=10,
        )
    )
    db.commit()
    return found


def preparation(db, repository, owner):
    found = published_source(db, owner)
    return repository.prepare(owner, EducationalPromptBuilder().build(request(), found))


def test_claim_owner_single_send_and_no_open_transaction(claim_database):
    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    claim = GenerationClaimRepository(db)
    with pytest.raises(HTTPException) as error:
        claim.claim(identifier, owners[1], TARGET, 5)
    assert error.value.status_code == 404
    payload = claim.claim(identifier, owners[0], TARGET, 5)
    assert payload.prompt and not db.in_transaction()
    with pytest.raises(HTTPException) as error:
        claim.claim(identifier, owners[0], TARGET, 5)
    assert error.value.status_code == 409
    record = db.get(ContentGeneration, identifier)
    assert record.status == "generating" and record.generation_started_at is not None


def test_global_daily_limit_survives_new_repository_and_covers_other_owner(claim_database):
    db, repository, owners = claim_database
    first = preparation(db, repository, owners[0])
    second = preparation(db, repository, owners[1])
    GenerationClaimRepository(db).claim(first, owners[0], TARGET, 1)
    repository.finish(first, owners[0], status="failed", error_code="llm_timeout")
    with pytest.raises(HTTPException) as error:
        GenerationClaimRepository(db).claim(second, owners[1], TARGET, 1)
    assert error.value.status_code == 429
    assert db.get(ContentGeneration, second).status == "prepared"


def test_missing_source_prevents_claim(claim_database):
    db, repository, owners = claim_database
    prepared = EducationalPromptBuilder().build(request(), retrieval())
    identifier = repository.prepare(owners[0], prepared)
    with pytest.raises(HTTPException) as error:
        GenerationClaimRepository(db).claim(identifier, owners[0], TARGET, 5)
    assert error.value.status_code == 422
    assert db.get(ContentGeneration, identifier).generation_started_at is None


def test_abandoned_attempt_is_closed_without_resending_it(claim_database):
    db, repository, owners = claim_database
    first = preparation(db, repository, owners[0])
    second = preparation(db, repository, owners[0])
    claim = GenerationClaimRepository(db)
    claim.claim(first, owners[0], TARGET, 5)
    record = db.get(ContentGeneration, first)
    record.generation_started_at -= timedelta(seconds=100)
    db.commit()
    claim.claim(second, owners[0], TARGET, 5)
    db.expire_all()
    assert db.get(ContentGeneration, first).error_code == "generation_interrupted"
    assert not repository.finish(first, owners[0], status="failed", error_code="llm_timeout")


@pytest.mark.parametrize("outcome", ["valid", "invalid", "timeout"])
def test_cost_basis_is_durable_before_send_and_survives_failure(claim_database, outcome):
    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    basis = CostBasis(requested_model=TARGET.requested_model)
    GenerationClaimRepository(db).claim(identifier, owners[0], TARGET, 5, cost_basis=basis)
    db.expire_all()
    record = db.get(ContentGeneration, identifier)
    assert record.cost_basis == basis.model_dump(mode="json")
    assert record.estimated_cost is None
    trace = GenerationTraceService(repository, ResourceValidationService())
    if outcome == "timeout":
        trace.fail(identifier, owners[0], "llm_timeout")
    elif outcome == "invalid":
        with pytest.raises(ContentError):
            trace.finish(identifier, owners[0], response().model_copy(update={"text": "invalid"}))
    else:
        trace.finish(identifier, owners[0], response())
    detail = HistoryService(HistoryRepository(db)).detail(identifier, owners[0])
    assert detail.audit.cost_basis == basis
    assert detail.audit.estimated_cost == (None if outcome == "timeout" else 0)


@pytest.mark.parametrize("output_tokens", [10, None])
def test_incomplete_provider_metadata_reaches_private_history(
    claim_database, monkeypatch, output_tokens
):
    from types import SimpleNamespace
    from unittest.mock import Mock

    from app.modulos.contenidos.servicios.generate_preparation_service import (
        GeneratePreparationService,
    )
    from app.modulos.proveedores_ia.errors import ProviderError
    from app.modulos.proveedores_ia.schemas import FailureMetadata, TokenUsage

    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    metadata = FailureMetadata(
        provider="gemini",
        requested_model=TARGET.requested_model,
        usage=TokenUsage(input_tokens=20, output_tokens=output_tokens),
        latency_ms=7,
    )
    provider = Mock()
    provider.generate.side_effect = ProviderError("llm_incomplete", metadata=metadata)
    monkeypatch.setattr(
        "app.modulos.contenidos.servicios.generate_preparation_service.create_provider",
        lambda _: provider,
    )
    settings = SimpleNamespace(
        llm_enabled=True,
        llm_free_tier_confirmed=True,
        llm_default_provider="gemini",
        llm_model=TARGET.requested_model,
        llm_daily_request_limit=5,
        llm_max_input_chars=12000,
        llm_max_output_tokens=1024,
        llm_timeout_seconds=30,
    )
    result = GeneratePreparationService(
        GenerationClaimRepository(db),
        GenerationTraceService(repository, ResourceValidationService()),
        settings,
    ).generate(identifier, owners[0])
    assert result.status == "failed" and result.resource is None
    provider.generate.assert_called_once()
    detail = HistoryService(HistoryRepository(db)).detail(identifier, owners[0])
    assert detail.audit.usage == metadata.usage and detail.audit.latency_ms == 7
    assert detail.audit.error_code == "llm_incomplete"
    assert detail.audit.estimated_cost == (None if output_tokens is None else 0)
    assert detail.audit.execution_configuration.max_output_tokens == 1024


@pytest.mark.parametrize("outcome", ["valid", "invalid", "timeout"])
def test_execution_limits_persist_before_network_and_remain_after_terminal_state(
    claim_database, outcome
):
    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    configuration = ExecutionConfiguration(
        max_input_chars=12000, max_output_tokens=512, timeout_seconds=30
    )
    claim = GenerationClaimRepository(db)
    claim.claim(identifier, owners[0], TARGET, 5, execution_configuration=configuration)
    db.expire_all()
    assert not db.in_transaction()
    assert (
        db.get(ContentGeneration, identifier).execution_configuration == configuration.model_dump()
    )
    trace = GenerationTraceService(repository, ResourceValidationService())
    if outcome == "timeout":
        trace.fail(identifier, owners[0], "llm_timeout")
    elif outcome == "invalid":
        with pytest.raises(ContentError):
            trace.finish(identifier, owners[0], response().model_copy(update={"text": "invalid"}))
    else:
        trace.finish(identifier, owners[0], response())
    different_limits = configuration.model_copy(update={"max_output_tokens": 1024})
    with pytest.raises(HTTPException) as error:
        claim.claim(identifier, owners[0], TARGET, 5, execution_configuration=different_limits)
    assert error.value.status_code == 409
    detail = HistoryService(HistoryRepository(db)).detail(identifier, owners[0])
    assert detail.audit.execution_configuration == configuration
    with pytest.raises(HTTPException):
        HistoryService(HistoryRepository(db)).detail(identifier, owners[1])


def test_rejected_claim_does_not_attach_execution_limits(claim_database):
    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    configuration = ExecutionConfiguration(
        max_input_chars=12000, max_output_tokens=1024, timeout_seconds=30
    )
    with pytest.raises(HTTPException):
        GenerationClaimRepository(db).claim(
            identifier, owners[1], TARGET, 5, execution_configuration=configuration
        )
    detail = HistoryService(HistoryRepository(db)).detail(identifier, owners[0])
    assert detail.audit.execution_configuration is None
    assert detail.status == "prepared" and detail.audit.generation_started_at is None


def test_saved_limits_match_gemini_payload_and_not_later_settings(claim_database, monkeypatch):
    import json

    import httpx
    from pydantic import SecretStr

    from app.configuracion.settings import Settings
    from app.modulos.contenidos.servicios.generate_preparation_service import (
        GeneratePreparationService,
    )
    from app.modulos.proveedores_ia.gemini.gemini_provider import GeminiProvider
    from app.modulos.proveedores_ia.servicios.request_limiter import RequestLimiter

    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    settings = Settings(
        _env_file=None,
        llm_enabled=True,
        llm_free_tier_confirmed=True,
        llm_model=TARGET.requested_model,
        gemini_api_key=SecretStr("fictitious-integration-key"),
        llm_max_input_chars=12000,
        llm_max_output_tokens=1024,
        llm_timeout_seconds=30,
    )
    sent = []

    def respond(http_request):
        sent.append(json.loads(http_request.content))
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"finishReason": "STOP", "content": {"parts": [{"text": response().text}]}}
                ],
                "usageMetadata": {"promptTokenCount": 20, "candidatesTokenCount": 10},
            },
        )

    provider = GeminiProvider(
        settings, transport=httpx.MockTransport(respond), limiter=RequestLimiter()
    )
    monkeypatch.setattr(
        "app.modulos.contenidos.servicios.generate_preparation_service.create_provider",
        lambda _: provider,
    )
    result = GeneratePreparationService(
        GenerationClaimRepository(db),
        GenerationTraceService(repository, ResourceValidationService()),
        settings,
    ).generate(identifier, owners[0])
    assert result.status == "succeeded" and len(sent) == 1
    settings.llm_max_output_tokens = 512
    db.expire_all()
    configuration = (
        HistoryService(HistoryRepository(db))
        .detail(identifier, owners[0])
        .audit.execution_configuration
    )
    assert configuration.max_output_tokens == sent[0]["generationConfig"]["maxOutputTokens"] == 1024
    assert configuration.max_input_chars == 12000 and configuration.timeout_seconds == 30


@pytest.mark.parametrize(
    "change", ["withdraw", "republish", "course", "permission", "text", "revision"]
)
def test_changed_source_rejected_before_quota_reservation(claim_database, change):
    db, repository, owners = claim_database
    identifier = preparation(db, repository, owners[0])
    record = db.get(ContentGeneration, identifier)
    from uuid import UUID

    source = record.sources_snapshot[0]
    document = db.get(Document, UUID(source["document_id"]))
    if change == "withdraw":
        document.published_at = None
    elif change == "republish":
        document.published_at = datetime.now(UTC)
    elif change == "course":
        document.course = "probabilidad y estadística"
    elif change == "permission":
        document.permission_recorded_at = None
    elif change == "revision":
        document.embedding_revision = "obsoleta"
    else:
        db.get(DocumentChunk, UUID(source["id"])).text = "X" * len(source["text"])
    db.commit()
    with pytest.raises(HTTPException) as error:
        GenerationClaimRepository(db).claim(identifier, owners[0], TARGET, 5)
    assert error.value.status_code == 422
    assert db.get(ContentGeneration, identifier).status == "prepared"
    assert db.get(ContentGeneration, identifier).generation_started_at is None
