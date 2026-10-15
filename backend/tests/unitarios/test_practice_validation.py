import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import create_app
from app.modulos.estudiantes.router import get_practice_service
from app.modulos.estudiantes.schemas import ANSWER_KEYS, CORRECT_OPTIONS, PracticeSubmission
from app.modulos.estudiantes.service import PracticeService
from app.nucleo.dependencias.auth import get_current_user


@pytest.mark.parametrize(
    "answers", [[], [0], [0, 2, 3, 1], [True, 2, 3], ["0", 2, 3], [0, -1, 3], [0, 2, 4]]
)
def test_rejects_incomplete_or_invalid_answers(answers):
    with pytest.raises(ValidationError):
        PracticeSubmission(id=uuid4(), version="derivadas-v1", answers=answers)


@pytest.mark.parametrize("extra", [{"score": 3}, {"owner_id": str(uuid4())}, {"version": "v2"}])
def test_rejects_forged_fields_or_version(extra):
    with pytest.raises(ValidationError):
        PracticeSubmission.model_validate(
            {"id": str(uuid4()), "version": "derivadas-v1", "answers": [0, 2, 3], **extra}
        )


def test_score_computed_by_server_and_reused_id_cannot_change_answers():
    submission = PracticeSubmission(id=uuid4(), version="derivadas-v1", answers=[0, 0, 3])
    repo = Mock()
    repo.save.return_value = SimpleNamespace(version=submission.version, answers=submission.answers)
    service = PracticeService(repo)
    owner = uuid4()
    service.save(owner, submission)
    repo.save.assert_called_once_with(owner, submission, 2)
    repo.save.return_value.answers = [0, 2, 3]
    with pytest.raises(HTTPException) as error:
        service.save(owner, submission)
    assert error.value.status_code == 409


def test_bank_version_and_answer_key_match_frontend():
    root = Path(__file__).resolve().parents[3]
    source = root / "frontend/src/app/modulos/estudiantes/modelos/practice-question.ts"
    if not source.exists():
        pytest.skip("El contenedor backend no incluye fuentes Angular")
    assert (
        tuple(map(int, re.findall(r"correctOption:\s*(\d+)", source.read_text(encoding="utf-8"))))
        == CORRECT_OPTIONS
    )
    service = source.parent.parent / "servicios/practice.service.ts"
    assert "PRACTICE_VERSION = 'derivadas-v1'" in service.read_text(encoding="utf-8")
    rules = source.with_name("practice-rules.ts").read_text(encoding="utf-8")
    assert tuple(map(int, re.findall(r"correctOption:\s*(\d+)", rules))) == ANSWER_KEYS["reglas-v1"]


def test_rules_score_and_cross_version_conflict():
    repo = Mock()
    submission = PracticeSubmission(id=uuid4(), version="reglas-v1", answers=[1, 0, 2])
    repo.save.return_value = SimpleNamespace(version=submission.version, answers=submission.answers)
    owner = uuid4()
    PracticeService(repo).save(owner, submission)
    repo.save.assert_called_once_with(owner, submission, 3)
    repo.save.return_value.version = "derivadas-v1"
    with pytest.raises(HTTPException) as error:
        PracticeService(repo).save(owner, submission)
    assert error.value.status_code == 409


def test_api_requires_session_and_client_header_and_limits_body():
    app = create_app()

    def missing():
        raise HTTPException(401, "Sin sesión")

    app.dependency_overrides[get_current_user] = missing
    service = Mock()
    app.dependency_overrides[get_practice_service] = lambda: service
    with TestClient(app) as client:
        assert client.get("/api/v1/practice/attempts").status_code == 401
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())
        payload = {"id": str(uuid4()), "version": "derivadas-v1", "answers": [0, 2, 3]}
        assert client.post("/api/v1/practice/attempts", json=payload).status_code == 403
        assert client.post("/api/v1/practice/attempts", content=b"x" * 17000).status_code == 413
        assert client.get("/api/v1/practice/attempts?limit=21").status_code == 422
        service.save.assert_not_called()
