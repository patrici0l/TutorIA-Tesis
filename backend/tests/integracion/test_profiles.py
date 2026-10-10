from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.main import create_app
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.integracion.test_content_trace_database import pytestmark as trace_marks
from tests.integracion.test_content_trace_database import trace_database as trace_database
from tests.unitarios.test_profile_validation import SAMPLE

pytestmark = trace_marks
HEADERS = {"X-TutorIA-Client": "web"}


def test_profile_api_durable_immutable_owner_and_validation(trace_database):
    db, _, owners = trace_database
    app = create_app()
    owner = db.get(User, owners[0])
    app.dependency_overrides[get_current_user] = lambda: owner
    app.dependency_overrides[get_session] = lambda: db
    with TestClient(app) as client:
        assert client.post("/api/v1/profiles", json=SAMPLE).status_code == 403
        first = client.post("/api/v1/profiles", json=SAMPLE, headers=HEADERS)
        assert first.status_code == 201
        data = first.json()
        assert data["data_kind"] == "synthetic" and "owner_id" not in data
        assert first.headers["Cache-Control"] == "no-store"
        identifier = data["id"]
        assert client.get(f"/api/v1/profiles/{identifier}").json() == data
        second = client.post(
            "/api/v1/profiles", json={**SAMPLE, "performance": 80}, headers=HEADERS
        )
        assert second.status_code == 201 and second.json()["id"] != identifier
        assert client.get(f"/api/v1/profiles/{identifier}").json()["performance"] == 42
        page = client.get("/api/v1/profiles?limit=1").json()
        assert page["total"] == 2 and len(page["items"]) == 1
        later = client.get("/api/v1/profiles?limit=1&offset=1").json()
        assert later["items"][0]["id"] != page["items"][0]["id"]
        assert "frequent_errors" not in page["items"][0]
        assert (
            client.post(
                "/api/v1/profiles", json={**SAMPLE, "owner_id": str(owners[1])}, headers=HEADERS
            ).status_code
            == 422
        )
        assert (
            client.post("/api/v1/profiles", content=b"x" * 17000, headers=HEADERS).status_code
            == 413
        )
        assert client.get("/api/v1/profiles?limit=21").status_code == 422
        assert client.get("/api/v1/profiles?offset=-1").status_code == 422
        assert client.get("/api/v1/profiles/not-uuid").status_code == 422
        owner = db.get(User, owners[1])
        for candidate in (identifier, str(uuid4())):
            assert client.get(f"/api/v1/profiles/{candidate}").status_code == 404
        assert client.get("/api/v1/profiles").json()["total"] == 0
        owner.rol = "admin"
        assert client.get(f"/api/v1/profiles/{identifier}").status_code == 404
        owner.rol = "student"
        assert client.get("/api/v1/profiles").status_code == 403
        assert client.post("/api/v1/profiles", json=SAMPLE, headers=HEADERS).status_code == 403
    assert UUID(identifier)


def test_profile_create_limit_before_persistence(trace_database):
    import pytest
    from fastapi import HTTPException

    from app.modulos.perfiles.repositorios.profile_repository import ProfileRepository
    from app.modulos.perfiles.schemas import ProfileRequest
    from app.modulos.perfiles.servicios.profile_service import ProfileService
    from app.nucleo.seguridad.rate_limiter import AuthRateLimiter

    db, _, owners = trace_database
    repository = ProfileRepository(db)
    service = ProfileService(repository, AuthRateLimiter(limit=1))
    service.create(ProfileRequest(**SAMPLE), owners[0])
    with pytest.raises(HTTPException) as error:
        service.create(ProfileRequest(**SAMPLE), owners[0])
    assert error.value.status_code == 429
    assert repository.page(owners[0], 0, 10)[1] == 1
