import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.modulos.contenidos.adaptation_schemas import PreparationRequest
from app.modulos.contenidos.servicios.adaptation_service import AdaptationService
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from tests.fixtures.content_reference import request, retrieval
from tests.unitarios.test_profile_validation import SAMPLE


def profile(level="low", **values):
    return SimpleNamespace(
        id=uuid4(),
        created_at=datetime.now(UTC),
        schema_version="performance-profile-v1",
        payload={**SAMPLE, "mastery_level": level, **values},
    )


@pytest.mark.parametrize(
    "level,difficulty", [("low", "basic"), ("medium", "intermediate"), ("high", "advanced")]
)
@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_same_topic_distinct_policy_and_private_prompt(level, difficulty, kind):
    record, owner = profile(level, performance=100), uuid4()
    repository = Mock(owned=Mock(return_value=record))
    original = request(kind, difficulty="intermediate")
    effective, snapshot = AdaptationService(repository).adapt(original, record.id, owner)
    repository.owned.assert_called_once_with(record.id, owner)
    assert effective.difficulty == difficulty and original.difficulty == "intermediate"
    assert effective.resource_type == kind
    assert snapshot.profile.performance == 100 and snapshot.profile.mastery_level == level
    prepared = EducationalPromptBuilder().build(effective, retrieval(), adaptation=snapshot)
    data = json.loads(prepared.generation_request.prompt)
    assert data["request"]["difficulty"] == difficulty
    assert data["focus_errors"] == SAMPLE["frequent_errors"]
    assert (
        "student_id" not in data["request"]
        and str(record.id) not in prepared.generation_request.prompt
    )
    assert "perfil ni datos" not in prepared.generation_request.instructions
    assert "datos no confiables" in prepared.generation_request.instructions
    assert prepared.prompt_version == "educational-rag-profile-v2"


def test_topic_mismatch_and_missing_profile_rejected_before_preparation():
    record = profile(topic="Límites")
    service = AdaptationService(Mock(owned=Mock(return_value=record)))
    with pytest.raises(HTTPException) as error:
        service.adapt(request(), record.id, uuid4())
    assert error.value.status_code == 422
    service.profiles.owned.return_value = None
    with pytest.raises(HTTPException) as error:
        service.adapt(request(), record.id, uuid4())
    assert error.value.status_code == 404


def test_no_errors_no_localized_diagnosis_and_manual_compatibility():
    record = profile(frequent_errors=[])
    effective, snapshot = AdaptationService(Mock(owned=Mock(return_value=record))).adapt(
        request(topic=" DERIVADAS "), record.id, uuid4()
    )
    assert snapshot.focus_errors == [] and "localizado" not in snapshot.reason
    manual = EducationalPromptBuilder().build(request(), retrieval())
    assert manual.adaptation is None and manual.prompt_version == "educational-rag-v1"
    assert "focus_errors" not in json.loads(manual.generation_request.prompt)


def test_client_cannot_send_profile_or_policy():
    for forged in ({"profile": SAMPLE}, {"adaptation": {}}, {"profile_id": "invalid"}):
        with pytest.raises(ValidationError):
            PreparationRequest(**request().model_dump(), **forged)
