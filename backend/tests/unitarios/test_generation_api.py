from unittest.mock import Mock
from uuid import uuid4

from test_documents import HEADERS
from test_documents import document_app as document_app

from app.configuracion.settings import Settings
from app.modulos.contenidos.router import get_generation_service
from app.modulos.contenidos.servicios.generate_preparation_service import GeneratePreparationService


def test_generation_route_roles_csrf_and_safe_response(document_app):
    client, _, app, owner, _, _ = document_app
    identifier = uuid4()
    service = Mock()
    service.generate.return_value = {
        "id": identifier,
        "status": "failed",
        "message": "Cuota agotada.",
        "resource": None,
    }
    app.dependency_overrides[get_generation_service] = lambda: service
    url = f"/api/v1/content/{identifier}/generate"
    assert client.post(url).status_code == 403
    response = client.post(url, headers=HEADERS)
    assert response.status_code == 200 and response.headers["Cache-Control"] == "no-store"
    assert set(response.json()) == {"id", "status", "message", "resource"}
    service.generate.assert_called_once_with(identifier, owner.id)
    assert client.post(url, json={"model": "unauthorized"}, headers=HEADERS).status_code == 422
    assert client.post(url, content=b"x" * 17000, headers=HEADERS).status_code == 413
    owner.rol = "student"
    assert client.post(url, headers=HEADERS).status_code == 403
    app.dependency_overrides.clear()
    assert client.post(url, headers=HEADERS).status_code == 401


def test_disabled_generation_never_claims_or_sends():
    import pytest
    from fastapi import HTTPException

    claim, trace = Mock(), Mock()
    service = GeneratePreparationService(claim, trace, Settings(_env_file=None))
    with pytest.raises(HTTPException) as error:
        service.generate(uuid4(), uuid4())
    assert error.value.status_code == 503
    claim.claim.assert_not_called()
