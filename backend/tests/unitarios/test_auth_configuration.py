from fastapi.testclient import TestClient

from app.configuracion.settings import get_settings
from app.main import create_app


def test_public_auth_configuration_only_exposes_mode(monkeypatch):
    client = TestClient(create_app())
    for mode in ("mock", "cas"):
        monkeypatch.setenv("AUTH_MODE", mode)
        get_settings.cache_clear()
        response = client.get("/api/v1/auth/config")
        assert response.status_code == 200
        assert response.json() == {"auth_mode": mode}
        assert response.headers["Cache-Control"] == "no-store"
        assert "set-cookie" not in response.headers
