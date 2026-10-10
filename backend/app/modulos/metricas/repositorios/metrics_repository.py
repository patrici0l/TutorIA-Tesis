from uuid import UUID

from sqlalchemy import BigInteger, func, or_, select
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
        # Una sola consulta/snapshot; filtrar propietario antes de agregar.
        result = self.db.execute(select(*fields).where(row.owner_id == owner)).mappings().one()
        self.db.commit()
        return dict(result)
