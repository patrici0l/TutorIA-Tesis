from uuid import uuid4

from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.main import create_app
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.integracion.test_content_trace_database import pytestmark as pytestmark
from tests.integracion.test_content_trace_database import trace_database as trace_database


def test_private_durable_idempotent_practice_history(trace_database):
    db, _, owners = trace_database
    app = create_app()
    current = db.get(User, owners[0])
    current.rol = "student"
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_session] = lambda: db
    headers = {"X-TutorIA-Client": "web"}
    payload = {"id": str(uuid4()), "version": "derivadas-v1", "answers": [0, 0, 3]}
    with TestClient(app) as client:
        assert client.get("/api/v1/practice/attempts").json()["best_score"] is None
        first = client.post("/api/v1/practice/attempts", json=payload, headers=headers)
        assert first.status_code == 200
        assert first.json()["score"] == 2
        assert "owner_id" not in first.json()
        assert first.headers["cache-control"] == "no-store"
        db.expire_all()
        repeat = client.post("/api/v1/practice/attempts", json=payload, headers=headers)
        assert repeat.json() == first.json()
        changed = {**payload, "answers": [0, 2, 3]}
        assert (
            client.post("/api/v1/practice/attempts", json=changed, headers=headers).status_code
            == 409
        )
        changed["id"] = str(uuid4())
        assert (
            client.post("/api/v1/practice/attempts", json=changed, headers=headers).json()["score"]
            == 3
        )
        page = client.get("/api/v1/practice/attempts?limit=1").json()
        assert page["total"] == 2 and page["best_score"] == 3 and len(page["items"]) == 1
        earlier = client.get("/api/v1/practice/attempts?offset=1&limit=1").json()
        assert earlier["items"][0]["id"] != page["items"][0]["id"]
        current = db.get(User, owners[1])
        current.rol = "admin"
        assert client.get("/api/v1/practice/attempts").json()["total"] == 0
        assert (
            client.post("/api/v1/practice/attempts", json=payload, headers=headers).status_code
            == 200
        )
        assert client.get("/api/v1/practice/attempts").json()["total"] == 1
        rules = {"id": str(uuid4()), "version": "reglas-v1", "answers": [1, 0, 2]}
        result = client.post("/api/v1/practice/attempts", json=rules, headers=headers)
        assert result.status_code == 200 and result.json()["score"] == 3
        db.expire_all()
        history = client.get("/api/v1/practice/attempts").json()
        assert {item["version"] for item in history["items"]} == {"derivadas-v1", "reglas-v1"}
