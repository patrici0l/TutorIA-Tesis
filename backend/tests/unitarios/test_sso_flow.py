from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.base_datos.models.base import Base
from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.main import create_app
from app.modulos.autenticacion.models import AuthSession, LoginAttempt
from app.modulos.autenticacion.router import get_cas_validator
from app.modulos.autenticacion.schemas import InstitutionalIdentity
from app.modulos.autenticacion.servicios.cas_validation_service import CasValidationError
from app.modulos.usuarios.models import User


@pytest.fixture
def auth_app():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    app = create_app()

    def sessions():
        with Session(engine, expire_on_commit=False) as db:
            yield db

    app.dependency_overrides[get_session] = sessions
    with TestClient(app, base_url="http://localhost:4200", follow_redirects=False) as client:
        yield client, engine, app
    engine.dispose()


def mock_login(client):
    start = client.get("/api/v1/auth/login")
    assert start.status_code == 302
    result = client.get(start.headers["location"])
    assert result.status_code == 303
    assert result.headers["location"].endswith("/inicio")
    return start, result


def test_mock_flow_cookie_provisioning_and_logout(auth_app):
    client, engine, _ = auth_app
    assert client.get("/api/v1/auth/me").status_code == 401
    _, callback = mock_login(client)
    cookie = callback.headers.get_list("set-cookie")[-1]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Path=/api/v1" in cookie
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200 and me.json()["auth_mode"] == "mock"
    user = me.json()["user"]
    assert user["institutional_email"] == "estudiante.demo@example.org"
    assert set(user) == {
        "id",
        "institutional_email",
        "institutional_id",
        "nombre",
        "apellido",
        "rol",
        "activo",
        "created_at",
        "last_login",
    }
    assert me.headers["cache-control"] == "no-store"
    token = client.cookies.get("tutoria_session")
    with Session(engine) as db:
        assert db.scalar(select(AuthSession)).digest != token
        assert db.scalar(select(User)).institutional_id == "mock:student-001"
    assert client.post("/api/v1/auth/logout").status_code == 403
    assert (
        client.post("/api/v1/auth/logout", headers={"X-TutorIA-Client": "web"}).status_code == 204
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    client.cookies.set("tutoria_session", token, domain="localhost.local", path="/api/v1")
    assert client.get("/api/v1/auth/me").status_code == 401


def test_repeat_login_updates_user_and_rotates_session(auth_app):
    client, engine, _ = auth_app
    mock_login(client)
    first = client.get("/api/v1/auth/me").json()["user"]
    old_token = client.cookies.get("tutoria_session")
    mock_login(client)
    second = client.get("/api/v1/auth/me").json()["user"]
    assert first["id"] == second["id"]
    assert second["last_login"] >= first["last_login"]
    assert client.cookies.get("tutoria_session") != old_token
    with Session(engine) as db:
        assert len(db.scalars(select(User)).all()) == 1
        assert len(db.scalars(select(AuthSession)).all()) == 1


def test_callback_requires_matching_browser_state_and_single_use(auth_app):
    client, _, _ = auth_app
    start = client.get("/api/v1/auth/login")
    state = client.cookies.get("tutoria_login_state")
    url = start.headers["location"]
    client.cookies.clear()
    assert "access_denied" in client.get(url).headers["location"]
    client.cookies.set("tutoria_login_state", state, domain="localhost.local", path="/api/v1/auth")
    assert client.get(url).headers["location"].endswith("/inicio")
    client.cookies.set("tutoria_login_state", state, domain="localhost.local", path="/api/v1/auth")
    assert "access_denied" in client.get(url).headers["location"]


def test_expired_attempt_rejected(auth_app):
    client, engine, _ = auth_app
    start = client.get("/api/v1/auth/login")
    with Session(engine) as db:
        db.scalar(select(LoginAttempt)).expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()
    assert "access_denied" in client.get(start.headers["location"]).headers["location"]


@pytest.mark.parametrize("condition", ["expired", "disabled", "wrong_mode"])
def test_invalid_session_rejected(auth_app, condition):
    client, engine, _ = auth_app
    mock_login(client)
    with Session(engine) as db:
        session = db.scalar(select(AuthSession))
        if condition == "expired":
            session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        if condition == "disabled":
            db.scalar(select(User)).activo = False
        if condition == "wrong_mode":
            session.mode = "cas"
        db.commit()
    assert client.get("/api/v1/auth/me").status_code == 401


def test_disabled_user_not_reactivated_by_new_login(auth_app):
    client, engine, _ = auth_app
    mock_login(client)
    with Session(engine) as db:
        db.scalar(select(User)).activo = False
        db.commit()
    start = client.get("/api/v1/auth/login")
    assert "access_denied" in client.get(start.headers["location"]).headers["location"]


def test_browser_cannot_choose_identity_or_use_old_endpoints(auth_app):
    client, _, _ = auth_app
    start = client.get("/api/v1/auth/login?email=attacker@est.ups.edu.ec&role=admin")
    client.get(start.headers["location"] + "&email=attacker@est.ups.edu.ec")
    user = client.get("/api/v1/auth/me").json()["user"]
    assert user["rol"] == "student" and user["institutional_email"] == "estudiante.demo@example.org"
    assert (
        client.post("/api/v1/auth/login", json={"email": "x", "password": "x"}).status_code == 405
    )
    assert client.post("/api/v1/auth/register").status_code == 404
    assert client.post("/api/v1/auth/refresh").status_code == 404


def test_cas_callback_uses_server_validator_and_exact_service(auth_app):
    client, _, app = auth_app
    settings = get_settings()
    settings.auth_mode = "cas"
    settings.auth_cookie_secure = True
    settings.auth_callback_url = "https://tutoria.example.org/api/v1/auth/callback"
    settings.auth_frontend_url = "https://tutoria.example.org/inicio"
    settings.auth_login_url = "https://tutoria.example.org/login"
    settings.cas_login_url = "https://sso.example.org/login"
    settings.cas_validate_url = "https://sso.example.org/validate"
    client.base_url = "https://tutoria.example.org"
    calls = []

    class Validator:
        def validate(self, ticket, service):
            calls.append((ticket, service))
            return InstitutionalIdentity(
                institutional_email="fictional@est.ups.edu.ec",
                nombre="Prueba",
                apellido="CAS",
                rol="student",
            )

    app.dependency_overrides[get_cas_validator] = lambda: Validator()
    start = client.get("/api/v1/auth/login")
    service = parse_qs(urlsplit(start.headers["location"]).query)["service"][0]
    callback = client.get(service + "&ticket=ST-fictional")
    assert callback.status_code == 303 and callback.headers["location"].endswith("/inicio")
    assert calls == [("ST-fictional", service)]
    assert "Secure" in callback.headers.get_list("set-cookie")[-1]
    assert client.get("/api/v1/auth/me").json()["auth_mode"] == "cas"


def test_invalid_cas_ticket_does_not_create_session(auth_app):
    client, engine, app = auth_app
    start = client.get("/api/v1/auth/login")
    get_settings().auth_mode = "cas"
    with Session(engine) as db:
        db.scalar(select(LoginAttempt)).mode = "cas"
        db.commit()

    class Reject:
        def validate(self, ticket, service):
            raise CasValidationError()

    app.dependency_overrides[get_cas_validator] = lambda: Reject()
    result = client.get(start.headers["location"] + "&ticket=invalid")
    assert "access_denied" in result.headers["location"]
    assert client.cookies.get("tutoria_session") is None


def test_models_have_no_password_fields():
    assert "password" not in User.__table__.columns
    assert "password_hash" not in User.__table__.columns
