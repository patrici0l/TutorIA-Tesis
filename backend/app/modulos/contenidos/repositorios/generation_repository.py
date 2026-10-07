import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modulos.contenidos.models import ContentGeneration
from app.modulos.proveedores_ia.schemas import GenerationTarget
from app.modulos.rag.prompts.educational_prompt import PreparedContent


class GenerationRepository:
    def __init__(self, db: Session):
        self.db = db

    def prepare(
        self, owner: UUID, prepared: PreparedContent, target: GenerationTarget | None = None
    ):
        record = ContentGeneration(
            provider=target.provider if target else None,
            requested_model=target.requested_model if target else None,
            owner_id=owner,
            request_snapshot=prepared.request.model_dump(mode="json", exclude_none=True),
            sources_snapshot=json.loads(prepared.sources_json),
            retrieval_snapshot=json.loads(prepared.retrieval_json),
            instructions=prepared.generation_request.instructions,
            prompt=prepared.generation_request.prompt,
            prompt_version=prepared.prompt_version,
            prompt_sha256=prepared.prompt_sha256,
        )
        self.db.add(record)
        self.db.flush()
        identifier = record.id
        self.db.commit()  # La preparación debe ser durable antes de cualquier llamada externa.
        return identifier

    def owned_snapshot(self, identifier: UUID, owner: UUID):
        row = self.db.execute(
            select(
                ContentGeneration.request_snapshot,
                ContentGeneration.sources_snapshot,
                ContentGeneration.status,
                ContentGeneration.provider,
                ContentGeneration.requested_model,
            ).where(ContentGeneration.id == identifier, ContentGeneration.owner_id == owner)
        ).first()
        self.db.commit()  # No conservar transacción de lectura durante inferencia futura.
        return None if row is None else tuple(row)

    def finish(self, identifier: UUID, owner: UUID, **values) -> bool:
        result = self.db.execute(
            update(ContentGeneration)
            .where(
                ContentGeneration.id == identifier,
                ContentGeneration.owner_id == owner,
                ContentGeneration.status.in_(["prepared", "generating"]),
            )
            .values(**values, completed_at=datetime.now(UTC))
            .execution_options(synchronize_session=False)
        )
        self.db.commit()
        self.db.expire_all()
        return result.rowcount == 1
