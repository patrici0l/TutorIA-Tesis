# Reserva el cupo global en PostgreSQL antes de permitir una llamada externa.
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.contenidos.execution_schemas import ExecutionConfiguration
from app.modulos.contenidos.models import ContentGeneration
from app.modulos.documentos.models import Document
from app.modulos.proveedores_ia.schemas import GenerationRequest, GenerationTarget
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.repositorios.search_repository import SearchRepository


class GenerationClaimRepository:
    def __init__(self, db: Session):
        self.db = db

    def daily_usage(self):
        now = self.db.scalar(select(func.clock_timestamp())).astimezone(UTC)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used = self.db.scalar(
            select(func.count())
            .select_from(ContentGeneration)
            .where(ContentGeneration.generation_started_at >= day_start)
        )
        return used, day_start + timedelta(days=1)

    def claim(
        self,
        identifier: UUID,
        owner: UUID,
        target: GenerationTarget,
        daily_limit: int,
        cost_basis: CostBasis | None = None,
        execution_configuration: ExecutionConfiguration | None = None,
    ):
        try:
            # Serializa reservas de todos los docentes para respetar el cupo compartido.
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
            snapshots = record.sources_snapshot
            courses = {source.get("course") for source in snapshots}
            if len(courses) != 1 or None in courses:
                raise HTTPException(422, "Vuelve a preparar el recurso indicando su asignatura.")
            course = next(iter(courses))
            sources = {UUID(source["document_id"]) for source in snapshots}
            available = set(
                self.db.scalars(
                    select(Document.id)
                    .join(DocumentChunk)
                    .where(
                        Document.id.in_(sources),
                        *SearchRepository.eligibility(owner, course),
                    )
                )
            )
            if not sources or sources != available:
                raise HTTPException(422, "Las fuentes cambiaron. Vuelve a preparar el recurso.")
            # Una preparación antigua no autoriza enviar texto retirado o reprocesado.
            for source in snapshots:
                current = self.db.execute(
                    select(Document, DocumentChunk)
                    .join(DocumentChunk)
                    .where(
                        Document.id == UUID(source["document_id"]),
                        DocumentChunk.id == UUID(source["id"]),
                        *SearchRepository.eligibility(owner, course),
                    )
                ).first()
                if current is None or (
                    current[0].sha256 != source["document_sha256"]
                    or not source.get("published_at")
                    or current[0].published_at != datetime.fromisoformat(source["published_at"])
                    or current[0].processing_version != source["processing_version"]
                    or current[1].source_sha256 != source["source_sha256"]
                    or current[1].text != source["text"]
                ):
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
                raise HTTPException(
                    429, "Se alcanzó el límite diario de generación. Continúa mañana."
                )
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
            record.cost_basis = cost_basis.model_dump(mode="json") if cost_basis else None
            record.execution_configuration = (
                execution_configuration.model_dump(mode="json") if execution_configuration else None
            )
            # Confirma la reserva antes de salir a red; un fallo posterior también consume cupo.
            self.db.commit()
            return payload
        except Exception:
            self.db.rollback()
            raise
