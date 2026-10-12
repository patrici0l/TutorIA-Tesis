import pytest

from app.configuracion.settings import Settings


def test_special_characters_in_password_are_preserved():
    settings = Settings(_env_file=None, db_password="test@:/#%value", database_url="")
    assert settings.get_database_url().password == "test@:/#%value"
    assert "test@:/#%value" not in repr(settings)


def test_postgres_url_uses_psycopg():
    settings = Settings(_env_file=None, database_url="postgresql://user:pass@localhost/test")
    assert settings.get_database_url().drivername == "postgresql+psycopg"


@pytest.mark.parametrize("port", ["invalid", "65536", "-1", "0"])
def test_auth_rejects_invalid_callback_and_frontend_ports(port):
    settings = Settings(
        _env_file=None,
        auth_callback_url=f"http://localhost:{port}/api/v1/auth/callback",
        auth_frontend_url=f"http://localhost:{port}/inicio",
        auth_login_url=f"http://localhost:{port}/login",
    )
    with pytest.raises(ValueError, match="puerto de autenticación"):
        settings.validate_auth()


def test_auth_accepts_consistent_alternate_local_port():
    Settings(
        _env_file=None,
        auth_callback_url="http://localhost:4201/api/v1/auth/callback",
        auth_frontend_url="http://localhost:4201/inicio",
        auth_login_url="http://localhost:4201/login",
    ).validate_auth()


@pytest.mark.parametrize("field", ["cas_login_url", "cas_validate_url"])
def test_auth_rejects_invalid_cas_endpoint_port(field):
    settings = Settings(
        _env_file=None,
        auth_mode="cas",
        auth_cookie_secure=True,
        auth_callback_url="https://tutoria.example.org/api/v1/auth/callback",
        auth_frontend_url="https://tutoria.example.org/inicio",
        auth_login_url="https://tutoria.example.org/login",
        cas_login_url="https://sso.example.org/login",
        cas_validate_url="https://sso.example.org/validate",
    )
    setattr(settings, field, "https://sso.example.org:invalid/endpoint")
    with pytest.raises(ValueError, match="puerto de autenticación"):
        settings.validate_auth()


def test_auth_rejects_cas_ticket_parameter_collision_with_browser_state():
    with pytest.raises(ValueError, match="nombre reservado state"):
        Settings(_env_file=None, cas_ticket_parameter="state").validate_auth()


def test_auth_preserves_custom_cas_parameter_names():
    Settings(
        _env_file=None, cas_service_parameter="ups_service", cas_ticket_parameter="ups_ticket"
    ).validate_auth()
