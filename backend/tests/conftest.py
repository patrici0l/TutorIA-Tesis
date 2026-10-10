import pytest

from app.configuracion.settings import get_settings


@pytest.fixture(autouse=True)
def test_auth_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("AUTH_MODE", "mock")
    monkeypatch.setenv("AUTH_COOKIE_SECURE", "false")
    monkeypatch.setenv("AUTH_MOCK_USER", "student")
    monkeypatch.setenv("AUTH_CALLBACK_URL", "http://localhost:4200/api/v1/auth/callback")
    monkeypatch.setenv("AUTH_FRONTEND_URL", "http://localhost:4200/inicio")
    monkeypatch.setenv("AUTH_LOGIN_URL", "http://localhost:4200/login")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
