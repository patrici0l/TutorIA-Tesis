from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import update

from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.contenidos.errors import ContentError
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
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
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


def preparation(db, repository, owner):
    found = retrieval()
    hit = found.results[0]
    db.add(
        Document(
            id=hit.document_id,
            owner_id=owner,
            filename=hit.filename,
            title=hit.document_title,
            mime_type="text/plain",
            size_bytes=10,
            sha256=hit.document_sha256,
        )
    )
    db.commit()
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
