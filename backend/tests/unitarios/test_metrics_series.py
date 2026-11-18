from datetime import UTC, date, datetime
from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy.dialects import postgresql

from app.modulos.metricas.repositorios.metrics_repository import MetricsRepository


def test_daily_series_preserves_zero_unknown_and_filters_owner_and_local_dates():
    owner = uuid4()
    aggregate = Mock()
    aggregate.mappings.return_value.one.return_value = {
        "observed_at": datetime(2026, 11, 16, 2, tzinfo=UTC)
    }
    point = {"day": date(2026, 11, 15), "records": 1, "input_tokens": 0,
             "output_tokens": None, "latency_ms": None, "latency_records": 0}
    series = Mock()
    series.mappings.return_value.all.return_value = [point]
    db = Mock()
    db.execute.side_effect = [aggregate, series]
    result = MetricsRepository(db).summary(owner)
    assert result["daily"] == [point]
    statement = db.execute.call_args_list[1].args[0].compile(dialect=postgresql.dialect())
    assert owner in statement.params.values()
    assert date(2026, 10, 17) in statement.params.values()
    assert "GROUP BY" in str(statement)
    assert "coalesce" in str(statement)
    db.commit.assert_called_once()
