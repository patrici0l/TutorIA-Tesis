from datetime import UTC, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.modulos.contenidos.models import ContentGeneration
from app.modulos.documentos.models import Document
from app.modulos.proveedores_ia.schemas import GenerationRequest, GenerationTarget


class GenerationClaimRepository:
    def __init__(self, db: Session):
        self.db = db

    def claim(self, identifier: UUID, owner: UUID, target: GenerationTarget, daily_limit: int):
        try:
            self.db.execute(text("SELECT pg_advisory_xact_lock(739117)"))
            now = self.db.scalar(select(func.clock_timestamp())).astimezone(UTC)
            self.db.execute(
                update(ContentGeneration)
                .where(
                    ContentGeneration.status == "generating",
                    ContentGeneration.generation_started_at < now - timedelta(seconds=90),
                )
                .values(status="failed", error_code="generation_interrupted", completed_at=now)
            )
            record = self.db.scalar(
                select(ContentGeneration).where(
                    ContentGeneration.id == identifier,
                    ContentGeneration.owner_id == owner,
                )
            )
            if record is None:
                raise HTTPException(404, "Preparación no disponible.")
            if record.status != "prepared":
                raise HTTPException(
                    409, "Esta preparación ya fue enviada. Prepara un nuevo recurso para continuar."
                )
            sources = {UUID(source["document_id"]) for source in record.sources_snapshot}
            available = set(
                self.db.scalars(
                    select(Document.id).where(
                        Document.id.in_(sources),
                        Document.owner_id == owner,
                        Document.deleted_at.is_(None),
                    )
                )
            )
            if not sources or sources != available:
                raise HTTPException(422, "Las fuentes cambiaron. Vuelve a preparar el recurso.")
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            count = self.db.scalar(
                select(func.count())
                .select_from(ContentGeneration)
                .where(
                    ContentGeneration.generation_started_at >= day_start,
                )
            )
            if count >= daily_limit:
                raise HTTPException(429, "Se alcanzó el límite diario de pruebas. Continúa mañana.")
            recent = self.db.scalar(
                select(func.count())
                .select_from(ContentGeneration)
                .where(
                    ContentGeneration.generation_started_at > now - timedelta(seconds=60),
                )
            )
            busy = self.db.scalar(
                select(func.count())
                .select_from(ContentGeneration)
                .where(
                    ContentGeneration.status == "generating",
                )
            )
            if recent or busy:
                raise HTTPException(
                    429,
                    "Espera un minuto antes de generar otro recurso.",
                    headers={"Retry-After": "60"},
                )
            payload = GenerationRequest(instructions=record.instructions, prompt=record.prompt)
            record.status = "generating"
            record.generation_started_at = now
            record.provider = target.provider
            record.requested_model = target.requested_model
            self.db.commit()
            return payload
        except Exception:
            self.db.rollback()
            raise
