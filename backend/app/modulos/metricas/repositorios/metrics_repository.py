# Agrega estados y consumo propio sin convertir valores desconocidos en cero.
from datetime import timedelta, timezone
from uuid import UUID

from sqlalchemy import BigInteger, Date, cast, func, or_, select
from sqlalchemy.orm import Session

from app.modulos.contenidos.models import ContentGeneration


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def summary(self, owner: UUID) -> dict:
        row = ContentGeneration
        # Las trazas antiguas pueden tener resultado sin fecha de reserva del cupo.
        executed = or_(row.generation_started_at.is_not(None), row.status != "prepared")
        fields = [
            func.now().label("observed_at"),
            func.count().label("total_records"),
            func.count().filter(executed).label("execution_records"),
            func.count(row.generation_started_at).label("reserved_attempts"),
            func.count(row.estimated_cost).filter(executed).label("cost_known_records"),
            func.count(row.latency_ms).filter(executed).label("latency_known_records"),
            func.avg(row.latency_ms).filter(executed).label("latency_average"),
            func.min(row.latency_ms).filter(executed).label("latency_min"),
            func.max(row.latency_ms).filter(executed).label("latency_max"),
        ]
        for state in ("prepared", "generating", "succeeded", "failed"):
            fields.append(func.count().filter(row.status == state).label(state))
        for name in ("input_tokens", "output_tokens", "total_tokens"):
            value = row.usage[name].as_string().cast(BigInteger)
            fields.extend(
                [
                    func.sum(value).filter(executed).label(f"{name}_sum"),
                    func.count(value).filter(executed).label(f"{name}_known"),
                ]
            )
        # Filtrar por propietario antes de agregar.
        result = self.db.execute(select(*fields).where(row.owner_id == owner)).mappings().one()
        day = cast(
            func.timezone(
                "America/Guayaquil",
                func.coalesce(row.generation_started_at, row.completed_at, row.created_at),
            ),
            Date,
        )
        daily = (
            self.db.execute(
                select(
                    day.label("day"),
                    func.count().label("records"),
                    func.sum(row.usage["input_tokens"].as_string().cast(BigInteger))
                    .filter(executed)
                    .label("input_tokens"),
                    func.sum(row.usage["output_tokens"].as_string().cast(BigInteger))
                    .filter(executed)
                    .label("output_tokens"),
                    func.avg(row.latency_ms).filter(executed).label("latency_ms"),
                    func.count(row.latency_ms).filter(executed).label("latency_records"),
                )
                .where(
                    row.owner_id == owner,
                    day
                    >= result["observed_at"].astimezone(timezone(timedelta(hours=-5))).date()
                    - timedelta(days=29),
                )
                .group_by(day)
                .order_by(day)
            )
            .mappings()
            .all()
        )
        self.db.commit()
        return {**dict(result), "daily": [dict(item) for item in daily]}
