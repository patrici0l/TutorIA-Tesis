from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.main import create_app
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.integracion.test_content_trace_database import pytestmark as pytestmark
from tests.integracion.test_content_trace_database import trace_database as trace_database


def test_assignment_lifecycle_permissions_and_private_attempts(trace_database):
    db, _, owners = trace_database
    students = [
        User(
            institutional_email=f"learner-{uuid4().hex}@example.org",
            nombre="Estudiante",
            apellido="Prueba",
            rol="student",
            activo=True,
            last_login=datetime.now(UTC),
        )
        for _ in range(2)
    ]
    db.add_all(students)
    db.flush()
    teacher = db.get(User, owners[0])
    other_teacher = db.get(User, owners[1])
    current = teacher
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_session] = lambda: db
    headers = {"X-TutorIA-Client": "web"}
    payload = {
        "id": str(uuid4()),
        "student_email": students[0].institutional_email,
        "title": "Repasar reglas",
        "version": "reglas-v1",
        "instructions": "Revisa cada explicación.",
    }
    base = "/api/v1/practice/assignments"
    with TestClient(app) as client:
        assert client.post(base, json=payload).status_code == 403
        first = client.post(base, json=payload, headers=headers)
        assert first.status_code == 200, first.text
        assert first.json()["attempts"] == 0 and first.json()["best_score"] is None
        assert first.headers["cache-control"] == "no-store"
        assert client.post(base, json=payload, headers=headers).json() == first.json()
        assert (
            client.post(base, json={**payload, "title": "Otro"}, headers=headers).status_code == 409
        )
        identifier = first.json()["id"]
        current = other_teacher
        assert client.get(base).json()["total"] == 0
        assert client.get(base + "/" + identifier).status_code == 404
        assert client.post(base, json=payload, headers=headers).status_code == 409
        current = students[1]
        assert client.get(base + "/" + identifier).status_code == 404
        assert client.post(base, json=payload, headers=headers).status_code == 403
        attempt = {
            "id": str(uuid4()),
            "version": "reglas-v1",
            "answers": [1, 0, 2],
            "assignment_id": identifier,
        }
        assert (
            client.post("/api/v1/practice/attempts", json=attempt, headers=headers).status_code
            == 404
        )
        current = students[0]
        assert client.get(base).json()["total"] == 1
        wrong = {**attempt, "version": "derivadas-v1"}
        assert (
            client.post("/api/v1/practice/attempts", json=wrong, headers=headers).status_code == 409
        )
        result = client.post("/api/v1/practice/attempts", json=attempt, headers=headers)
        assert result.status_code == 200 and result.json()["score"] == 3
        assert (
            client.post("/api/v1/practice/attempts", json=attempt, headers=headers).json()
            == result.json()
        )
        # The same attempt cannot be moved into/out of an assignment.
        assert (
            client.post(
                "/api/v1/practice/attempts",
                json={**attempt, "assignment_id": None},
                headers=headers,
            ).status_code
            == 409
        )
        free = {**attempt, "id": str(uuid4()), "assignment_id": None}
        assert (
            client.post("/api/v1/practice/attempts", json=free, headers=headers).status_code == 200
        )
        current = teacher
        db.expire_all()
        detail = client.get(base + "/" + identifier).json()
        assert detail["attempts"] == 1 and detail["best_score"] == 3
        assert "answers" not in detail
        assert client.get("/api/v1/practice/attempts").json()["total"] == 0
        assert (
            client.post(
                base,
                json={**payload, "id": str(uuid4()), "student_email": teacher.institutional_email},
                headers=headers,
            ).status_code
            == 422
        )
        assert client.get(base + "?limit=21").status_code == 422
        assert client.post(base, content=b"x" * 17000, headers=headers).status_code == 413

        def missing():
            raise HTTPException(401, "Sin sesión")

        app.dependency_overrides[get_current_user] = missing
        assert client.get(base).status_code == 401
        assert client.get(base + "/" + identifier).status_code == 401
