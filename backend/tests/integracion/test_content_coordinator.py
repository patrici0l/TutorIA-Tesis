from unittest.mock import Mock

import pytest

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.servicios.generate_content_service import GenerateContentService
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationTarget
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from tests.fixtures.content_reference import request, retrieval
from tests.integracion.test_content_trace_database import (
    pytestmark as trace_marks,
)
from tests.integracion.test_content_trace_database import (
    response,
)
from tests.integracion.test_content_trace_database import (
    trace_database as trace_database,
)

pytestmark = trace_marks


@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_coordinator_commits_before_network_and_validates_each_resource(trace_database, kind):
    db, repository, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(kind), retrieval())
    preparer, provider = Mock(), Mock()
    preparer.prepare.return_value = prepared
    original_prepare = repository.prepare
    identifiers = []

    def persist(*args):
        identifier = original_prepare(*args)
        identifiers.append(identifier)
        return identifier

    def generate(value):
        assert not db.in_transaction()
        snapshot = repository.owned_snapshot(identifiers[0], owners[0])
        assert snapshot[2:] == ("prepared", "gemini", "model-test-v1")
        assert repository.owned_snapshot(identifiers[0], owners[1]) is None
        assert value == prepared.generation_request
        assert not db.in_transaction()
        return response(kind)

    repository.prepare = persist
    provider.generate.side_effect = generate
    service = GenerateContentService(
        preparer,
        repository,
        provider,
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    outcome = service.generate(request(kind), owners[0])
    assert outcome.resource.resource_type == kind and outcome.error_code is None
    assert db.get(ContentGeneration, outcome.id).status == "succeeded"
    provider.generate.assert_called_once()


@pytest.mark.parametrize("code", ["llm_timeout", "llm_rate_limit", "llm_incomplete"])
def test_provider_failure_is_durable_without_retry(trace_database, code):
    db, repository, owners = trace_database
    preparer, provider = Mock(), Mock()
    preparer.prepare.return_value = EducationalPromptBuilder().build(request(), retrieval())
    provider.generate.side_effect = ProviderError(code)
    service = GenerateContentService(
        preparer,
        repository,
        provider,
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    outcome = service.generate(request(), owners[0])
    record = db.get(ContentGeneration, outcome.id)
    assert outcome.error_code == code and outcome.resource is None
    assert record.status == "failed" and record.error_code == code
    assert record.resource is None and record.usage is None
    provider.generate.assert_called_once()


def test_no_sources_never_call_provider(trace_database):
    _, repository, owners = trace_database
    preparer, provider = Mock(), Mock()
    preparer.prepare.side_effect = ContentError("content_no_sources")
    service = GenerateContentService(
        preparer,
        repository,
        provider,
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    with pytest.raises(ContentError, match="content_no_sources"):
        service.generate(request(), owners[0])
    provider.generate.assert_not_called()


def test_invalid_output_is_not_published_and_consumption_is_kept(trace_database):
    db, repository, owners = trace_database
    preparer, provider = Mock(), Mock()
    preparer.prepare.return_value = EducationalPromptBuilder().build(request(), retrieval())
    provider.generate.return_value = response(payload={"bad": "output"})
    service = GenerateContentService(
        preparer,
        repository,
        provider,
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    outcome = service.generate(request(), owners[0])
    record = db.get(ContentGeneration, outcome.id)
    assert outcome.error_code == "content_invalid_output" and outcome.resource is None
    assert record.status == "failed" and record.resource is None
    assert record.usage["input_tokens"] == 20


def test_unexpected_provider_exception_marks_interruption(trace_database):
    db, repository, owners = trace_database
    preparer, provider = Mock(), Mock()
    preparer.prepare.return_value = EducationalPromptBuilder().build(request(), retrieval())
    provider.generate.side_effect = RuntimeError("synthetic interruption")
    service = GenerateContentService(
        preparer,
        repository,
        provider,
        GenerationTarget(provider="gemini", requested_model="model-test-v1"),
    )
    original_prepare = repository.prepare
    identifiers = []

    def persist(*args):
        identifier = original_prepare(*args)
        identifiers.append(identifier)
        return identifier

    repository.prepare = persist
    with pytest.raises(RuntimeError, match="synthetic interruption"):
        service.generate(request(), owners[0])
    record = db.get(ContentGeneration, identifiers[0])
    assert record.status == "failed" and record.error_code == "generation_interrupted"
    provider.generate.assert_called_once()
