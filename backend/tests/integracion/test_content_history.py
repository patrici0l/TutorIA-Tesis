from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import update

from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.history_repository import HistoryRepository
from app.modulos.contenidos.servicios.history_service import HistoryService
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from tests.fixtures.content_reference import request, resource, retrieval
from tests.integracion.test_content_trace_database import pytestmark as trace_marks
from tests.integracion.test_content_trace_database import trace_database as trace_database

pytestmark = trace_marks


def test_history_private_pagination_snapshots_without_live_documents(trace_database):
    db, writer, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(), retrieval())
    identifiers = [writer.prepare(owners[0], prepared) for _ in range(3)]
    writer.prepare(owners[1], prepared)
    service = HistoryService(HistoryRepository(db))
    first = service.page(owners[0], 0, 2)
    second = service.page(owners[0], 2, 2)
    assert first.total == second.total == 3
    assert len(first.items) == 2 and len(second.items) == 1
    assert {item.id for item in first.items + second.items} == set(identifiers)
    assert not set(item.id for item in first.items).intersection(item.id for item in second.items)
    assert set(first.items[0].model_dump()) == {
        "id",
        "topic",
        "resource_type",
        "difficulty",
        "status",
        "created_at",
        "completed_at",
    }
    # No existe un documento vivo para esta fixture: el detalle usa el snapshot original.
    detail = service.detail(identifiers[0], owners[0])
    assert detail.preparation.sources[0].text == retrieval().results[0].text
    assert detail.resource is None and detail.status == "prepared"
    assert '"prompt":' not in detail.model_dump_json()
    assert '"instructions":' not in detail.model_dump_json()
    assert "owner_id" not in detail.model_dump_json()
    assert detail.audit.prompt_sha256 == prepared.prompt_sha256
    assert detail.audit.prompt_version == prepared.prompt_version
    assert detail.audit.retrieval.embedding_revision == retrieval().embedding_revision
    assert detail.audit.usage is None and detail.audit.latency_ms is None
    for identifier in (identifiers[0], uuid4()):
        with pytest.raises(HTTPException) as error:
            service.detail(identifier, owners[1])
        assert error.value.status_code == 404
    assert service.page(owners[0], 99, 2).items == []


def test_history_failed_and_generating_are_not_retried_or_mutated(trace_database):
    db, writer, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(), retrieval())
    identifier = writer.prepare(owners[0], prepared)
    db.execute(
        update(ContentGeneration)
        .where(ContentGeneration.id == identifier)
        .values(status="generating")
    )
    db.commit()
    service = HistoryService(HistoryRepository(db))
    assert service.detail(identifier, owners[0]).status == "generating"
    assert writer.finish(identifier, owners[0], status="failed", error_code="llm_timeout")
    for _ in range(2):
        detail = service.detail(identifier, owners[0])
        assert detail.status == "failed" and detail.resource is None
        assert detail.completed_at is not None and detail.message
        assert detail.audit.error_code == "llm_timeout"
        assert detail.audit.usage is None and detail.audit.estimated_cost is None


def test_history_audit_preserves_reported_zero_partial_usage_and_safe_errors(trace_database):
    db, writer, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(), retrieval())
    identifier = writer.prepare(owners[0], prepared)
    assert writer.finish(
        identifier,
        owners[0],
        status="succeeded",
        resource=resource(),
        provider="gemini",
        requested_model="model-test-v1",
        model_version="model-test-v1-001",
        usage={"input_tokens": 0},
        latency_ms=0,
    )
    service = HistoryService(HistoryRepository(db))
    detail = service.detail(identifier, owners[0])
    assert detail.audit.provider == "gemini"
    assert detail.audit.model_version == "model-test-v1-001"
    assert detail.audit.usage.input_tokens == 0
    assert detail.audit.usage.total_tokens is None
    assert detail.audit.latency_ms == 0 and detail.audit.estimated_cost is None
    assert detail.audit.generation_started_at is None  # Traza inicial, sin reserva persistente.
    failed = writer.prepare(owners[0], prepared)
    assert writer.finish(failed, owners[0], status="failed", error_code="private-unknown-error")
    assert service.detail(failed, owners[0]).audit.error_code is None
    assert "private-unknown-error" not in service.detail(failed, owners[0]).model_dump_json()
