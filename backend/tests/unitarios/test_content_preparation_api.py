from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from test_documents import HEADERS
from test_documents import document_app as document_app

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.router import get_preparation_service
from app.modulos.contenidos.servicios.preparation_service import PreparationService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter
from tests.fixtures.content_reference import request, retrieval

URL = "/api/v1/content/prepare"


def service():
    repository = Mock()
    repository.prepare.return_value = uuid4()
    preparer = PrepareContentService(
        SimpleNamespace(search=lambda *_: retrieval()), EducationalPromptBuilder()
    )
    return PreparationService(preparer, repository, 12000, AuthRateLimiter(limit=5))


def test_api_authorization_safe_response_and_body_limit(document_app):
    client, _, app, owner, _, _ = document_app
    actual = service()
    app.dependency_overrides[get_preparation_service] = lambda: actual
    payload = request().model_dump(exclude_none=True)
    assert client.post(URL, json=payload).status_code == 403
    response = client.post(URL, json=payload, headers=HEADERS)
    assert response.status_code == 201
    assert response.headers["Cache-Control"] == "no-store"
    result = response.json()
    assert result["status"] == "prepared" and result["sources"][0]["citation_id"] == "S1"
    assert set(result) == {
        "id",
        "status",
        "topic",
        "learning_objective",
        "resource_type",
        "difficulty",
        "question_count",
        "sources",
        "adaptation",
    }
    assert actual.repository.prepare.call_args.args[0] == owner.id
    assert "prompt" not in result and "student_answer" not in result
    assert (
        client.post(URL, json={**payload, "owner_id": str(uuid4())}, headers=HEADERS).status_code
        == 422
    )
    oversized = client.post(URL, content=b"x" * 17000, headers=HEADERS)
    assert oversized.status_code == 413 and oversized.headers["Cache-Control"] == "no-store"
    owner.rol = "student"
    assert client.post(URL, json=payload, headers=HEADERS).status_code == 403
    app.dependency_overrides.clear()
    assert client.post(URL, json=payload, headers=HEADERS).status_code == 401


@pytest.mark.parametrize(
    "code,status",
    [("content_no_sources", 422), ("content_context_limit", 422), ("content_invalid_sources", 503)],
)
def test_preparation_errors_never_persist(code, status):
    actual = service()
    actual.preparer = Mock()
    actual.preparer.prepare.side_effect = ContentError(code)
    with pytest.raises(HTTPException) as error:
        actual.prepare(request(), uuid4())
    assert error.value.status_code == status
    actual.repository.prepare.assert_not_called()


def test_rate_limit_is_per_owner_before_inference():
    actual, owner = service(), uuid4()
    for _ in range(5):
        actual.prepare(request(), owner)
    with pytest.raises(HTTPException) as error:
        actual.prepare(request(), owner)
    assert error.value.status_code == 429 and error.value.headers["Retry-After"] == "60"
    assert actual.repository.prepare.call_count == 5
    actual.prepare(request(), uuid4())
    assert actual.repository.prepare.call_count == 6
