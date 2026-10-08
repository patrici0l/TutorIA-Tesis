from datetime import UTC, datetime

from sqlalchemy import update

from app.modulos.contenidos.models import ContentGeneration
from app.modulos.metricas.repositorios.metrics_repository import MetricsRepository
from app.modulos.metricas.servicios.metrics_service import MetricsService
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from tests.fixtures.content_reference import request, resource, retrieval
from tests.integracion.test_content_trace_database import pytestmark as trace_marks
from tests.integracion.test_content_trace_database import trace_database as trace_database

pytestmark = trace_marks


def test_metrics_empty_preserves_unknown_instead_of_zero(trace_database):
    db, _, owners = trace_database
    summary = MetricsService(MetricsRepository(db)).summary(owners[0])
    assert summary.total_records == summary.execution_records == 0
    assert summary.input_tokens.known_sum is None
    assert summary.total_tokens.known_sum is None
    assert summary.latency.known_average_ms is None
    assert summary.cost_unknown_records == 0
    assert summary.observed_at.tzinfo is not None


def test_metrics_private_mixed_states_partial_usage_and_legacy(trace_database):
    db, writer, owners = trace_database
    prepared = EducationalPromptBuilder().build(request(), retrieval())
    identifiers = [writer.prepare(owners[0], prepared) for _ in range(5)]
    foreign = writer.prepare(owners[1], prepared)
    # Cero conocido es distinto de null; total reportado no se infiere de entrada/salida.
    assert writer.finish(
        identifiers[0],
        owners[0],
        status="succeeded",
        resource=resource(),
        usage={"input_tokens": 0, "output_tokens": 10, "total_tokens": 14},
        latency_ms=100,
    )
    assert writer.finish(identifiers[1], owners[0], status="failed", error_code="llm_timeout")
    assert writer.finish(
        identifiers[2],
        owners[0],
        status="failed",
        error_code="content_invalid_output",
        usage={"input_tokens": 20},
        latency_ms=300,
    )
    assert writer.finish(
        foreign,
        owners[1],
        status="succeeded",
        resource=resource(),
        usage={"input_tokens": 999999},
        latency_ms=999999,
    )
    db.execute(
        update(ContentGeneration)
        .where(ContentGeneration.id.in_(identifiers[1:4]))
        .values(generation_started_at=datetime.now(UTC))
    )
    db.execute(
        update(ContentGeneration)
        .where(ContentGeneration.id == identifiers[3])
        .values(status="generating")
    )
    db.commit()
    service = MetricsService(MetricsRepository(db))
    for _ in range(2):
        summary = service.summary(owners[0])
        assert summary.total_records == 5
        assert (summary.prepared, summary.generating, summary.succeeded, summary.failed) == (
            1,
            1,
            1,
            2,
        )
        assert summary.execution_records == 4 and summary.reserved_attempts == 3
        assert summary.input_tokens.model_dump() == {
            "known_sum": 20,
            "known_records": 2,
            "unknown_records": 2,
        }
        assert summary.output_tokens.known_sum == 10
        assert summary.total_tokens.model_dump() == {
            "known_sum": 14,
            "known_records": 1,
            "unknown_records": 3,
        }
        assert summary.latency.known_average_ms == 200
        assert summary.latency.known_min_ms == 100 and summary.latency.known_max_ms == 300
        assert summary.latency.unknown_records == 2
        assert summary.cost_known_records == 0 and summary.cost_unknown_records == 4
        assert "owner_id" not in summary.model_dump_json()
        assert "prompt" not in summary.model_dump_json()
    assert service.summary(owners[1]).total_records == 1
