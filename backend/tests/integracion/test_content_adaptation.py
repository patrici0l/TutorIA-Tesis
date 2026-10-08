from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.main import create_app
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.contenidos.router import get_preparation_service
from app.modulos.contenidos.servicios.adaptation_service import AdaptationService
from app.modulos.contenidos.servicios.generate_preparation_service import GeneratePreparationService
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.preparation_service import PreparationService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.documentos.models import Document
from app.modulos.perfiles.repositorios.profile_repository import ProfileRepository
from app.modulos.perfiles.schemas import ProfileRequest
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter
from tests.fixtures.content_reference import request, retrieval
from tests.integracion.test_content_trace_database import pytestmark as trace_marks
from tests.integracion.test_content_trace_database import response
from tests.integracion.test_content_trace_database import trace_database as trace_database
from tests.integracion.test_generation_claim import claim_database as claim_database
from tests.unitarios.test_profile_validation import SAMPLE

pytestmark = trace_marks
HEADERS = {"X-TutorIA-Client": "web"}


def test_saved_adaptation_is_sent_once_with_fake_provider(claim_database, monkeypatch):
    db, repository, owners = claim_database
    profiles = ProfileRepository(db)
    record = profiles.create(ProfileRequest(**SAMPLE), owners[0])
    effective, adaptation = AdaptationService(profiles).adapt(request(), record.id, owners[0])
    found = retrieval()
    hit = found.results[0]
    db.add(
        Document(
            id=hit.document_id,
            owner_id=owners[0],
            filename=hit.filename,
            title=hit.document_title,
            mime_type="text/plain",
            size_bytes=10,
            sha256=hit.document_sha256,
        )
    )
    db.commit()
    prepared = EducationalPromptBuilder().build(effective, found, adaptation=adaptation)
    identifier = repository.prepare(owners[0], prepared)
    provider = Mock()

    def generate(payload):
        assert not db.in_transaction()
        assert payload == prepared.generation_request
        return response()

    provider.generate.side_effect = generate
    monkeypatch.setattr(
        "app.modulos.contenidos.servicios.generate_preparation_service.create_provider",
        lambda _: provider,
    )
    settings = SimpleNamespace(
        llm_enabled=True,
        llm_free_tier_confirmed=True,
        llm_default_provider="gemini",
        llm_model="model-test-v1",
        llm_daily_request_limit=5,
    )
    service = GeneratePreparationService(
        GenerationClaimRepository(db),
        GenerationTraceService(repository, ResourceValidationService()),
        settings,
    )
    outcome = service.generate(identifier, owners[0])
    assert outcome.status == "succeeded"
    provider.generate.assert_called_once()
    stored = db.get(ContentGeneration, identifier)
    assert stored.adaptation_snapshot == adaptation.model_dump(mode="json")
    assert stored.resource["resource_type"] == "EXPLANATION"


def test_api_profile_snapshot_private_history_and_no_external_inference(trace_database):
    db, repository, owners = trace_database
    profiles = ProfileRepository(db)
    record = profiles.create(ProfileRequest(**SAMPLE), owners[0])
    identifier = record.id
    service = PreparationService(
        PrepareContentService(
            SimpleNamespace(search=lambda *_: retrieval()), EducationalPromptBuilder()
        ),
        repository,
        12000,
        AuthRateLimiter(limit=20),
        adaptation=AdaptationService(profiles),
    )
    app = create_app()
    owner = db.get(User, owners[0])
    app.dependency_overrides[get_session] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: owner
    app.dependency_overrides[get_preparation_service] = lambda: service
    payload = {
        **request(difficulty="advanced").model_dump(exclude_none=True),
        "profile_id": str(identifier),
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/content/prepare", json=payload, headers=HEADERS)
        assert response.status_code == 201 and response.headers["Cache-Control"] == "no-store"
        result = response.json()
        assert result["difficulty"] == "basic"
        assert result["adaptation"]["requested_difficulty"] == "advanced"
        generation = db.get(ContentGeneration, UUID(result["id"]))
        assert generation.provider is None and generation.generation_started_at is None
        assert generation.adaptation_snapshot == result["adaptation"]
        history = client.get(f"/api/v1/content/history/{result['id']}").json()
        assert history["preparation"]["adaptation"] == result["adaptation"]
        # Otra observación del mismo tema no cambia el snapshot previo.
        profiles.create(ProfileRequest(**{**SAMPLE, "mastery_level": "high"}), owners[0])
        assert client.get(f"/api/v1/content/history/{result['id']}").json() == history
        assert (
            client.post(
                "/api/v1/content/prepare", json={**payload, "topic": "Límites"}, headers=HEADERS
            ).status_code
            == 422
        )
        app.dependency_overrides[get_current_user] = lambda: db.get(User, owners[1])
        assert (
            client.post("/api/v1/content/prepare", json=payload, headers=HEADERS).status_code == 404
        )
        assert client.get(f"/api/v1/content/history/{result['id']}").status_code == 404
