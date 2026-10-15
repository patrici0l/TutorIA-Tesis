from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import delete, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.base_datos.session import get_engine, get_session
from app.main import create_app
from app.modulos.estudiantes.assignment_repository import AssignmentRepository
from app.modulos.estudiantes.assignment_schemas import AssignmentSubmission
from app.modulos.estudiantes.models import PracticeAssignment, PracticeAttempt
from app.modulos.estudiantes.repository import PracticeRepository
from app.modulos.estudiantes.schemas import PracticeSubmission
from app.modulos.estudiantes.service import PracticeService
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


@pytest.mark.parametrize("status", ["closed", "cancelled"])
def test_assignment_status_preserves_results_and_blocks_new_attempts(trace_database, status):
    db, _, owners = trace_database
    student = User(
        institutional_email=f"lifecycle-{uuid4().hex}@example.org",
        nombre="Prueba",
        apellido="Local",
        rol="student",
        activo=True,
        last_login=datetime.now(UTC),
    )
    db.add(student)
    db.flush()
    teacher = db.get(User, owners[0])
    current = teacher
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_session] = lambda: db
    headers = {"X-TutorIA-Client": "web"}
    base = "/api/v1/practice/assignments"
    attempts_url = "/api/v1/practice/attempts"
    payload = {
        "id": str(uuid4()),
        "student_email": student.institutional_email,
        "title": "Ciclo de prueba",
        "version": "reglas-v1",
    }
    with TestClient(app) as client:
        created = client.post(base, json=payload, headers=headers).json()
        assert created["status"] == "open" and created["status_changed_at"] is None
        url = base + "/" + created["id"] + "/status"
        change = {"status": status, "expected_status": "open"}
        assert client.post(url, json=change).status_code == 403
        assert (
            client.post(url, json={**change, "status": "deleted"}, headers=headers).status_code
            == 422
        )
        assert (
            client.post(
                url, json={**change, "teacher_id": str(teacher.id)}, headers=headers
            ).status_code
            == 422
        )
        assert client.post(url, content=b"x" * 17000, headers=headers).status_code == 413
        current = db.get(User, owners[1])
        assert client.post(url, json=change, headers=headers).status_code == 404
        current = student
        assert client.post(url, json=change, headers=headers).status_code == 403
        attempt = {
            "id": str(uuid4()),
            "version": "reglas-v1",
            "answers": [1, 0, 2],
            "assignment_id": created["id"],
        }
        saved = client.post(attempts_url, json=attempt, headers=headers).json()
        assert saved["score"] == 3
        current = teacher
        changed = client.post(url, json=change, headers=headers)
        assert changed.status_code == 200 and changed.headers["cache-control"] == "no-store"
        result = changed.json()
        assert result["status"] == status and result["status_changed_at"] is not None
        assert result["attempts"] == 1 and result["best_score"] == 3
        assert client.post(url, json=change, headers=headers).json() == result
        # A create retry must not reactivate an activity.
        assert client.post(base, json=payload, headers=headers).json()["status"] == status
        stale = {
            "expected_status": "open",
            "status": "cancelled" if status == "closed" else "closed",
        }
        assert client.post(url, json=stale, headers=headers).status_code == 409
        current = student
        assert client.get(base).json()["items"][0]["status"] == status
        assert client.post(attempts_url, json=attempt, headers=headers).json() == saved
        assert (
            client.post(
                attempts_url, json={**attempt, "answers": [0, 0, 0]}, headers=headers
            ).status_code
            == 409
        )
        new_attempt = {**attempt, "id": str(uuid4())}
        rejected = client.post(attempts_url, json=new_attempt, headers=headers)
        assert (
            rejected.status_code == 409 and "no admite nuevos intentos" in rejected.json()["detail"]
        )
        assert client.get(attempts_url).json()["total"] == 1
        assert (
            client.post(
                attempts_url, json={**new_attempt, "assignment_id": None}, headers=headers
            ).status_code
            == 200
        )
        current = teacher
        reopened = client.post(
            url, json={"status": "open", "expected_status": status}, headers=headers
        )
        assert reopened.status_code == 200 and reopened.json()["status"] == "open"
        current = student
        assert (
            client.post(
                attempts_url, json={**attempt, "id": str(uuid4())}, headers=headers
            ).status_code
            == 200
        )
        current = teacher
        assert client.get(base).json()["items"][0]["attempts"] == 2

        def missing():
            raise HTTPException(401, "Sin sesión")

        app.dependency_overrides[get_current_user] = missing
        assert client.post(url, json=change, headers=headers).status_code == 401


def test_close_and_save_serialize_across_database_connections():
    """Only these random synthetic rows are committed and removed for a real lock test."""
    engine = get_engine()
    teacher_id, student_id, assignment_id = uuid4(), uuid4(), uuid4()
    submission = PracticeSubmission(
        id=uuid4(),
        assignment_id=assignment_id,
        version="reglas-v1",
        answers=[1, 0, 2],
    )
    try:
        with Session(engine) as setup:
            setup.add_all(
                [
                    User(
                        id=identifier,
                        institutional_email=f"lock-{identifier}@example.org",
                        nombre="Prueba",
                        apellido="Bloqueo",
                        rol=role,
                        activo=True,
                        last_login=datetime.now(UTC),
                    )
                    for identifier, role in [(teacher_id, "teacher"), (student_id, "student")]
                ]
            )
            setup.commit()
            AssignmentRepository(setup).create(
                teacher_id,
                student_id,
                AssignmentSubmission(
                    id=assignment_id,
                    student_email=f"lock-{student_id}@example.org",
                    version="reglas-v1",
                    title="Actividad de prueba concurrente",
                ),
            )
        with Session(engine) as teacher_db, Session(engine) as student_db:
            assignments = AssignmentRepository(teacher_db)
            practice = PracticeService(PracticeRepository(student_db))
            locked = assignments.lock_owned(teacher_id, assignment_id)
            student_db.execute(text("SET LOCAL lock_timeout = '100ms'"))
            with pytest.raises(OperationalError) as blocked:
                practice.save(student_id, submission)
            assert blocked.value.orig.sqlstate == "55P03"
            student_db.rollback()
            assignments.change_status(locked, "closed")
            with pytest.raises(HTTPException) as closed:
                practice.save(student_id, submission)
            assert closed.value.status_code == 409
            student_db.rollback()

            assignments.change_status(assignments.lock_owned(teacher_id, assignment_id), "open")
            PracticeRepository(student_db).assignment(student_id, assignment_id)
            teacher_db.execute(text("SET LOCAL lock_timeout = '100ms'"))
            with pytest.raises(OperationalError) as blocked:
                assignments.lock_owned(teacher_id, assignment_id)
            assert blocked.value.orig.sqlstate == "55P03"
            teacher_db.rollback()
            assert practice.save(student_id, submission).score == 3
            assignments.change_status(assignments.lock_owned(teacher_id, assignment_id), "closed")
            assert practice.save(student_id, submission).score == 3
    finally:
        with Session(engine) as cleanup:
            cleanup.execute(
                delete(PracticeAttempt).where(PracticeAttempt.assignment_id == assignment_id)
            )
            cleanup.execute(
                delete(PracticeAssignment).where(PracticeAssignment.id == assignment_id)
            )
            cleanup.execute(delete(User).where(User.id.in_([teacher_id, student_id])))
            cleanup.commit()
