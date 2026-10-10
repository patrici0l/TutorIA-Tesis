import json
import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.base_datos.session import get_engine
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.proveedores_ia.schemas import GenerationResult, GenerationTarget, TokenUsage
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.usuarios.models import User
from tests.fixtures.content_reference import request, resource, retrieval

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Requiere PostgreSQL y migraciones"
    ),
]


@pytest.fixture
def trace_database():
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                connection, join_transaction_mode="create_savepoint", expire_on_commit=False
            ) as db:
                users = [
                    User(
                        institutional_email=f"trace-{uuid4().hex}@example.org",
                        nombre="Docente",
                        apellido="Sintético",
                        rol="teacher",
                        activo=True,
                        last_login=datetime.now(UTC),
                    )
                    for _ in range(2)
                ]
                db.add_all(users)
                db.flush()
                owners = [user.id for user in users]
                db.commit()
                repository = GenerationRepository(db)
                yield db, repository, owners
        finally:
            transaction.rollback()


def response(kind="EXPLANATION", payload=None):
    return GenerationResult(
        provider="gemini",
        requested_model="model-test-v1",
        model_version="model-test-v1-001",
        response_id="fictitious-test-response",
        text=json.dumps(payload or resource(kind)),
        usage=TokenUsage(input_tokens=20, output_tokens=10),
        latency_ms=1,
    )


def test_private_durable_source_prompt_snapshot_and_terminal_state(trace_database):
    db, repository, owners = trace_database
    found = retrieval()
    prepared = EducationalPromptBuilder().build(request(), found)
    identifier = repository.prepare(owners[0], prepared)
    assert not db.in_transaction()
    assert repository.owned_snapshot(identifier, owners[1]) is None
    assert not db.in_transaction()
    snapshot = repository.owned_snapshot(identifier, owners[0])
    assert snapshot[0]["resource_type"] == "EXPLANATION"
    assert snapshot[1][0]["id"] == str(found.results[0].id)
    record = db.get(ContentGeneration, identifier)
    assert record.prompt_sha256 == prepared.prompt_sha256
    assert record.prompt == prepared.generation_request.prompt
    assert record.instructions == prepared.generation_request.instructions
    assert record.retrieval_snapshot["embedding_revision"] == "rev-test"
    assert record.sources_snapshot[0]["text"] == found.results[0].text
    assert record.resource is None and record.estimated_cost is None
    found.results[0].text = "Cambio posterior que no altera la evidencia"
    assert record.sources_snapshot[0]["text"] != found.results[0].text
    db.commit()
    service = GenerationTraceService(repository, ResourceValidationService())
    with pytest.raises(ContentError, match="content_trace_unavailable"):
        service.finish(identifier, owners[1], response())
    validated = service.finish(identifier, owners[0], response())
    assert validated.resource_type == "EXPLANATION"
    record = db.get(ContentGeneration, identifier)
    assert record.status == "succeeded" and record.completed_at is not None
    assert record.usage["input_tokens"] == 20
    assert record.usage["reasoning_tokens"] is None and record.estimated_cost is None
    assert record.requested_model == "model-test-v1"
    db.commit()
    with pytest.raises(ContentError, match="content_trace_unavailable"):
        service.fail(identifier, owners[0], "llm_timeout")
    assert db.get(ContentGeneration, identifier).status == "succeeded"


@pytest.mark.parametrize("kind", ["EXERCISE", "QUIZ", "FEEDBACK"])
def test_all_resources_roundtrip_trace(trace_database, kind):
    db, repository, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(kind), retrieval())
    identifier = repository.prepare(owners[0], prepared)
    result = GenerationTraceService(repository, ResourceValidationService()).finish(
        identifier,
        owners[0],
        response(kind),
    )
    assert result.resource_type == kind
    assert db.get(ContentGeneration, identifier).resource["resource_type"] == kind


def test_invalid_output_records_safe_failure_and_known_usage(trace_database):
    db, repository, owners = trace_database
    identifier = repository.prepare(
        owners[0], EducationalPromptBuilder().build(request(), retrieval())
    )
    bad = resource()
    bad["summary"]["citations"] = ["S2"]
    service = GenerationTraceService(repository, ResourceValidationService())
    with pytest.raises(ContentError, match="content_invalid_citations"):
        service.finish(identifier, owners[0], response(payload=bad))
    record = db.get(ContentGeneration, identifier)
    assert record.status == "failed" and record.error_code == "content_invalid_citations"
    assert record.resource is None and record.usage["output_tokens"] == 10
    assert record.estimated_cost is None


def test_provider_failure_code_and_unknown_usage(trace_database):
    db, repository, owners = trace_database
    identifier = repository.prepare(
        owners[0], EducationalPromptBuilder().build(request(), retrieval())
    )
    service = GenerationTraceService(repository, ResourceValidationService())
    with pytest.raises(ContentError, match="content_invalid_error_code"):
        service.fail(identifier, owners[0], "secret-or-raw-provider-text")
    service.fail(identifier, owners[0], "llm_timeout")
    record = db.get(ContentGeneration, identifier)
    assert record.status == "failed" and record.resource is None
    assert record.error_code == "llm_timeout" and record.usage is None
    assert record.latency_ms is None and record.estimated_cost is None


def test_database_rejects_inconsistent_terminal_row(trace_database):
    db, repository, owners = trace_database
    identifier = repository.prepare(
        owners[0], EducationalPromptBuilder().build(request(), retrieval())
    )
    with pytest.raises(IntegrityError):
        db.execute(
            update(ContentGeneration)
            .where(ContentGeneration.id == identifier)
            .values(status="succeeded")
        )
        db.commit()
    db.rollback()
    assert (
        db.scalar(select(ContentGeneration.status).where(ContentGeneration.id == identifier))
        == "prepared"
    )


def test_preselected_model_is_preserved_when_provider_fails(trace_database):
    db, repository, owners = trace_database
    identifier = repository.prepare(
        owners[0],
        EducationalPromptBuilder().build(request(), retrieval()),
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    GenerationTraceService(repository, ResourceValidationService()).fail(
        identifier, owners[0], "llm_timeout"
    )
    record = db.get(ContentGeneration, identifier)
    assert record.provider == "gemini" and record.requested_model == "model-test-v1"
    assert record.status == "failed" and record.usage is None


def test_response_from_another_model_cannot_complete_trace(trace_database):
    db, repository, owners = trace_database
    identifier = repository.prepare(
        owners[0],
        EducationalPromptBuilder().build(request(), retrieval()),
        GenerationTarget(provider="gemini", requested_model="other-model-test"),
    )
    service = GenerationTraceService(repository, ResourceValidationService())
    with pytest.raises(ContentError, match="content_target_mismatch"):
        service.finish(identifier, owners[0], response())
    record = db.get(ContentGeneration, identifier)
    assert record.status == "failed" and record.error_code == "content_target_mismatch"
    assert record.requested_model == "other-model-test" and record.resource is None
