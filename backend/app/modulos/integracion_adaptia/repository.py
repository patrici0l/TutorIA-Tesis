from datetime import UTC, timedelta

from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.modulos.contenidos.repositorios.generation_usage import (
    active_generations,
    expire_interrupted,
    started_generations,
)
from app.modulos.integracion_adaptia.errors import IntegrationError
from app.modulos.integracion_adaptia.models import AdaptiaGeneration


def saved_response(record, payload_hash):
    if record is None:
        return None
    if record.payload_sha256 != payload_hash:
        raise IntegrationError(409, "INVALID_REQUEST", "X-Request-ID ya identifica otra solicitud.")
    if record.status == "succeeded":
        return record.response
    message = (
        "La solicitud está en curso; no se realizó otro envío."
        if record.status == "generating"
        else "La solicitud anterior falló; un nuevo envío requiere otro X-Request-ID."
    )
    raise IntegrationError(409, "INVALID_REQUEST", message)


class AdaptiaRepository:
    def __init__(self, db: Session):
        self.db = db

    def replay(self, request_id, payload_hash):
        try:
            record = self.db.get(AdaptiaGeneration, request_id)
            result = saved_response(record, payload_hash)
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def reserve(self, request, context, payload_hash, prompt_hash, provider, model, daily_limit):
        try:
            # El mismo bloqueo que la UI: una segunda vía HTTP no duplica el presupuesto.
            self.db.execute(text("SELECT pg_advisory_xact_lock(739117)"))
            now = self.db.scalar(select(func.clock_timestamp())).astimezone(UTC)
            expire_interrupted(self.db, now)
            record = self.db.get(AdaptiaGeneration, context.request_id, populate_existing=True)
            existing = saved_response(record, payload_hash)
            if existing is not None:
                self.db.commit()
                return existing
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if started_generations(self.db, day_start) >= daily_limit:
                raise IntegrationError(429, "RATE_LIMIT_EXCEEDED", "Se alcanzó el cupo diario.")
            if active_generations(self.db) or started_generations(
                self.db, now - timedelta(seconds=60)
            ):
                raise IntegrationError(
                    429,
                    "RATE_LIMIT_EXCEEDED",
                    "Espera un minuto antes de generar otra vez.",
                    headers={"Retry-After": "60"},
                )
            self.db.add(
                AdaptiaGeneration(
                    request_id=context.request_id,
                    payload_sha256=payload_hash,
                    request_snapshot=request.model_dump(mode="json"),
                    student_id_hash=request.student_id,
                    session_id=context.session_id,
                    prompt_version="adaptia-direct-v1",
                    prompt_sha256=prompt_hash,
                    provider=provider,
                    requested_model=model,
                    status="generating",
                    generation_started_at=now,
                )
            )
            self.db.commit()  # Trazabilidad durable antes de salir a red.
            return None
        except Exception:
            self.db.rollback()
            raise

    def finish(self, request_id, *, response=None, error_code=None, usage=None):
        from datetime import datetime

        try:
            result = self.db.execute(
                update(AdaptiaGeneration)
                .where(
                    AdaptiaGeneration.request_id == request_id,
                    AdaptiaGeneration.status == "generating",
                )
                .values(
                    status="failed" if error_code else "succeeded",
                    response=response,
                    error_code=error_code,
                    usage=usage,
                    completed_at=datetime.now(UTC),
                )
            )
            if result.rowcount != 1:
                raise IntegrationError(
                    503, "AI_SERVICE_UNAVAILABLE", "No se pudo confirmar la trazabilidad."
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
