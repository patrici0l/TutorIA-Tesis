from uuid import UUID

from app.modulos.metricas.repositorios.metrics_repository import MetricsRepository
from app.modulos.metricas.schemas import KnownTokenSum, LatencySummary, MetricsSummary


class MetricsService:
    def __init__(self, repository: MetricsRepository):
        self.repository = repository

    def summary(self, owner: UUID) -> MetricsSummary:
        values = self.repository.summary(owner)
        executed = values["execution_records"]
        tokens = {
            name: KnownTokenSum(
                known_sum=values[f"{name}_sum"],
                known_records=values[f"{name}_known"],
                unknown_records=executed - values[f"{name}_known"],
            )
            for name in ("input_tokens", "output_tokens", "total_tokens")
        }
        return MetricsSummary(
            observed_at=values["observed_at"],
            total_records=values["total_records"],
            prepared=values["prepared"],
            generating=values["generating"],
            succeeded=values["succeeded"],
            failed=values["failed"],
            reserved_attempts=values["reserved_attempts"],
            execution_records=executed,
            **tokens,
            latency=LatencySummary(
                known_average_ms=values["latency_average"],
                known_min_ms=values["latency_min"],
                known_max_ms=values["latency_max"],
                known_records=values["latency_known_records"],
                unknown_records=executed - values["latency_known_records"],
            ),
            cost_known_records=values["cost_known_records"],
            cost_unknown_records=executed - values["cost_known_records"],
        )
