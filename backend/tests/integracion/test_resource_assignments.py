from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.main import create_app
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.fixtures.content_reference import request, resource, retrieval
from tests.integracion.test_content_trace_database import (
    pytestmark as pytestmark,
)
from tests.integracion.test_content_trace_database import (
    response,
)
from tests.integracion.test_content_trace_database import (
    trace_database as trace_database,
)


@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_generated_integrals_can_be_assigned_privately_and_reopened(trace_database, kind):
    db, repository, owners = trace_database
    teacher, other = (db.get(User, owner) for owner in owners)
    student = User(
        institutional_email=f"resource-{uuid4().hex}@example.org",
        nombre="Estudiante",
        apellido="Sintético",
        rol="student",
        activo=True,
        last_login=datetime.now(UTC),
    )
    db.add(student)
    db.flush()
    content_request = request(kind).model_copy(update={"topic": "Integrales"})
    prepared = EducationalPromptBuilder().build(content_request, retrieval())
    resource_id = repository.prepare(teacher.id, prepared)
    current = teacher
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_session] = lambda: db
    headers = {"X-TutorIA-Client": "web"}
    base = "/api/v1/practice/assignments"
    payload = {
        "id": str(uuid4()),
        "student_email": student.institutional_email,
        "version": "resource-v1",
        "resource_id": str(resource_id),
        "title": "Integrales",
    }
    with TestClient(app) as client:
        # Preparation alone is not a published resource.
        assert client.post(base, json=payload, headers=headers).status_code == 404
        material = resource(kind)
        material["title"] = "Integrales"
        GenerationTraceService(repository, ResourceValidationService()).finish(
            resource_id, teacher.id, response(kind, material)
        )
        assert client.post(base, json=payload).status_code == 403
        for invalid in (
            {**payload, "resource_id": None},
            {**payload, "version": "reglas-v1"},
            {**payload, "resource": material},
        ):
            assert client.post(base, json=invalid, headers=headers).status_code == 422
        current = other
        assert client.post(base, json=payload, headers=headers).status_code == 404
        current = teacher
        created = client.post(base, json=payload, headers=headers)
        assert created.status_code == 200, created.text
        assert created.json()["resource_id"] == str(resource_id)
        assert client.post(base, json=payload, headers=headers).json() == created.json()
        assert (
            client.post(base, json={**payload, "title": "Otro"}, headers=headers).status_code == 409
        )
        url = base + "/" + payload["id"]
        current = other
        assert client.get(url).status_code == 404
        current = student
        assert client.post(base, json=payload, headers=headers).status_code == 403
        detail = client.get(url)
        assert detail.status_code == 200, detail.text
        data = detail.json()
        assert data["resource"] == material and len(data["sources"]) > 0
        assert not {"prompt", "adaptation_snapshot", "request_snapshot", "usage"} & data.keys()
        assert client.get(f"/api/v1/content/history/{resource_id}").status_code == 403
        assert client.get(base).json()["items"][0]["resource_id"] == str(resource_id)
        assert (
            client.post(
                "/api/v1/practice/attempts",
                json={
                    "id": str(uuid4()),
                    "version": "reglas-v1",
                    "answers": [1, 0, 2],
                    "assignment_id": payload["id"],
                },
                headers=headers,
            ).status_code
            == 409
        )
        current = teacher
        for status, expected in [("closed", "open"), ("open", "closed")]:
            assert (
                client.post(
                    url + "/status",
                    json={
                        "status": status,
                        "expected_status": expected,
                    },
                    headers=headers,
                ).status_code
                == 200
            )
        db.expire_all()
        current = student
        assert client.get(url).json()["resource"] == material
