from datetime import timedelta

from fastapi.testclient import TestClient

from app.base_datos.session import get_session
from app.configuracion.settings import Settings, get_settings
from app.main import create_app
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user
from tests.fixtures.content_reference import request, retrieval
from tests.integracion.test_content_trace_database import (
    pytestmark as pytestmark,
)
from tests.integracion.test_content_trace_database import (
    trace_database as trace_database,
)


def test_quota_counts_shared_reserved_requests_and_respects_utc_day(trace_database):
    db, repository, owners = trace_database
    counter = GenerationClaimRepository(db)
    baseline, reset = counter.daily_usage()
    for owner, started in [
        (owners[0], reset - timedelta(hours=1)),
        (owners[1], reset - timedelta(hours=2)),
        (owners[0], reset - timedelta(days=1, hours=1)),
    ]:
        identifier = repository.prepare(
            owner, EducationalPromptBuilder().build(request(), retrieval())
        )
        row = db.get(ContentGeneration, identifier)
        row.status = "failed"
        row.completed_at = started
        row.generation_started_at = started
        row.error_code = "llm_incomplete"
        db.commit()
    teacher = db.get(User, owners[0])
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: teacher
    app.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    # Route reads configured settings; assert limits from returned payload, not test machine env.
    with TestClient(app) as client:
        response = client.get("/api/v1/content/quota")
        assert response.status_code == 200, response.text
        assert response.headers["cache-control"] == "no-store"
        result = response.json()
        assert result["used"] == baseline + 2
        assert result["remaining"] == max(0, result["daily_limit"] - baseline - 2)
        assert result["resets_at"] == reset.isoformat().replace("+00:00", "Z")
        teacher.rol = "student"
        assert client.get("/api/v1/content/quota").status_code == 403
        app.dependency_overrides.pop(get_current_user)
        assert client.get("/api/v1/content/quota").status_code == 401
