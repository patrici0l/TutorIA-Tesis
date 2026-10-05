from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.v1.health_router import get_health_service
from app.main import create_app
from app.nucleo.utilidades.health_service import HealthService


@pytest.mark.parametrize("database,vector,status", [(True, True, 200), (True, False, 503)])
def test_health_contract(database, vector, status):
    repository = Mock()
    repository.check.return_value = (database, vector)
    app = create_app()
    app.dependency_overrides[get_health_service] = lambda: HealthService(repository)
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == status
    assert response.json()["database"] == "ok"
    assert response.json()["pgvector"] == ("ok" if vector else "unavailable")


def test_database_failure_does_not_expose_credentials(caplog):
    repository = Mock()
    repository.check.side_effect = OperationalError("secret-sentinel", {}, Exception("password"))
    app = create_app()
    app.dependency_overrides[get_health_service] = lambda: HealthService(repository)
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"
    assert "secret-sentinel" not in response.text + caplog.text


def test_openapi_documents_unavailability():
    with TestClient(create_app()) as client:
        schema = client.get("/api/v1/openapi.json").json()
    assert "503" in schema["paths"]["/api/v1/health"]["get"]["responses"]
