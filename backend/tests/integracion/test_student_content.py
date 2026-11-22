from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.main import create_app
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.documentos.models import Document
from app.modulos.rag.repositorios.search_repository import SearchRepository
from app.modulos.rag.router import get_search_service
from app.modulos.rag.servicios.model_spec import DIMENSIONS
from app.modulos.rag.servicios.search_service import SearchService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.fixtures.content_reference import request
from tests.integracion.test_content_trace_database import response
from tests.integracion.test_content_trace_database import trace_database as trace_database
from tests.integracion.test_generation_claim import claim_database as claim_database
from tests.integracion.test_generation_claim import published_source


class Worker:
    def encode(self, texts, mode):
        return {"vectors": [[1.0] + [0.0] * (DIMENSIONS - 1)], "token_counts": [10]}


@pytest.mark.parametrize("kind", ["EXPLANATION", "EXAMPLE", "HINT", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_student_complete_flow_and_privacy(claim_database, monkeypatch, kind):
    db, _, owners = claim_database
    teacher, other = [db.get(User, owner) for owner in owners]
    found = published_source(db, teacher.id)
    student = User(
        institutional_email=f"student-{uuid4().hex}@example.org",
        nombre="Alumno",
        apellido="Prueba",
        rol="student",
        activo=True,
        last_login=datetime.now(UTC),
    )
    db.add(student)
    db.commit()
    current = teacher
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_search_service] = lambda: SearchService(
        SearchRepository(db), Worker()
    )
    headers = {"X-Prototipo-Client": "web"}
    base = "/api/v1/learning"
    settings = get_settings()
    monkeypatch.setattr(settings, "gemini_api_key", SecretStr("synthetic-test-key"))
    monkeypatch.setattr(settings, "llm_enabled", True)
    monkeypatch.setattr(settings, "llm_default_provider", "gemini")
    monkeypatch.setattr(settings, "llm_free_tier_confirmed", True)
    monkeypatch.setattr(settings, "llm_model", "model-test-v1")
    calls = []

    class Provider:
        def generate(self, payload):
            calls.append(payload)
            return response(kind)

    monkeypatch.setattr(
        "app.modulos.contenidos.servicios.generate_preparation_service.create_provider",
        lambda _: Provider(),
    )
    with TestClient(app) as client:
        grant = {"student_email": student.institutional_email, "course": "Cálculo Diferencial"}
        assert client.post(base + "/access", json=grant).status_code == 403
        access = client.post(base + "/access", json=grant, headers=headers)
        assert access.status_code == 201, access.text
        access_id = access.json()["id"]
        assert client.post(base + "/access", json=grant, headers=headers).json()["id"] == access_id
        current = other
        assert client.get(base + "/access").json() == []
        assert client.delete(base + "/access/" + access_id, headers=headers).status_code == 404
        current = student
        assert client.get(base + "/access").status_code == 403
        assert client.get("/api/v1/documents").status_code == 403
        assert client.get(base + "/courses").json()[0]["id"] == access_id
        body = request(kind).model_dump(exclude_none=True)
        body.pop("course", None)
        body["access_id"] = access_id
        for injected in (
            {"course": "otra"},
            {"profile_id": str(uuid4())},
            {"owner_id": str(teacher.id)},
        ):
            assert (
                client.post(
                    base + "/prepare", json={**body, **injected}, headers=headers
                ).status_code
                == 422
            )
        assert (
            client.post(
                base + "/prepare", json={**body, "access_id": str(uuid4())}, headers=headers
            ).status_code
            == 403
        )
        prepared = client.post(base + "/prepare", json=body, headers=headers)
        assert prepared.status_code == 201, prepared.text
        identifier = prepared.json()["id"]
        assert prepared.json()["sources"][0]["document_id"] == str(found.results[0].document_id)
        record = db.get(ContentGeneration, UUID(identifier))
        assert record.owner_id == student.id
        assert str(record.learning_access_id) == access_id
        current = other
        assert client.get("/api/v1/content/history/" + identifier).status_code == 404
        current = student
        result = client.post(base + "/" + identifier + "/generate", json={}, headers=headers)
        assert result.status_code == 200, result.text
        assert result.json()["status"] == "succeeded", result.text
        assert len(calls) == 1
        assert (
            client.post(base + "/" + identifier + "/generate", json={}, headers=headers).status_code
            == 409
        )
        assert len(calls) == 1
        assert (
            client.get(base + "/history/" + identifier).json()["resource"]["resource_type"] == kind
        )


@pytest.mark.parametrize("withdraw", ["access", "document", "teacher"])
def test_revocation_blocks_pending_and_new_preparations(claim_database, monkeypatch, withdraw):
    db, _, owners = claim_database
    teacher = db.get(User, owners[0])
    found = published_source(db, teacher.id)
    student = db.get(User, owners[1])
    student.rol = "student"
    db.commit()
    current = teacher
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: current
    app.dependency_overrides[get_search_service] = lambda: SearchService(
        SearchRepository(db), Worker()
    )
    headers = {"X-Prototipo-Client": "web"}
    base = "/api/v1/learning"
    with TestClient(app) as client:
        access_id = client.post(
            base + "/access",
            headers=headers,
            json={
                "student_email": student.institutional_email,
                "course": found.results[0].course,
            },
        ).json()["id"]
        current = student
        body = request().model_dump(exclude_none=True)
        body.pop("course", None)
        body["access_id"] = access_id
        identifier = client.post(base + "/prepare", json=body, headers=headers).json()["id"]
        current = teacher
        if withdraw == "access":
            assert client.delete(base + "/access/" + access_id, headers=headers).status_code == 204
        elif withdraw == "document":
            db.get(Document, found.results[0].document_id).published_at = None
        else:
            teacher.activo = False
        db.commit()
        current = student
        assert client.post(base + "/prepare", json=body, headers=headers).status_code in {403, 422}
        from fastapi import HTTPException

        from app.modulos.contenidos.repositorios.generation_claim_repository import (
            GenerationClaimRepository,
        )
        from tests.integracion.test_generation_claim import TARGET

        with pytest.raises(HTTPException) as error:
            GenerationClaimRepository(db).claim(UUID(identifier), student.id, TARGET, 100)
        assert error.value.status_code in {403, 422}
        assert db.get(ContentGeneration, UUID(identifier)).status == "prepared"
