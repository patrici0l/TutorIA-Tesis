from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.contenidos.models import ContentGeneration


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def page(self, owner: UUID, offset: int, limit: int):
        # No cargar prompts/textos/recursos completos para una página de resúmenes.
        items = (
            self.db.execute(
                select(
                    ContentGeneration.id,
                    ContentGeneration.request_snapshot["topic"].as_string().label("topic"),
                    ContentGeneration.request_snapshot["resource_type"]
                    .as_string()
                    .label("resource_type"),
                    ContentGeneration.request_snapshot["difficulty"]
                    .as_string()
                    .label("difficulty"),
                    ContentGeneration.status,
                    ContentGeneration.created_at,
                    ContentGeneration.completed_at,
                )
                .where(ContentGeneration.owner_id == owner)
                .order_by(ContentGeneration.created_at.desc(), ContentGeneration.id.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        total = self.db.scalar(
            select(func.count())
            .select_from(ContentGeneration)
            .where(ContentGeneration.owner_id == owner)
        )
        return items, total

    def detail(self, identifier: UUID, owner: UUID):
        return (
            self.db.execute(
                select(
                    ContentGeneration.id,
                    ContentGeneration.request_snapshot,
                    ContentGeneration.sources_snapshot,
                    ContentGeneration.status,
                    ContentGeneration.created_at,
                    ContentGeneration.completed_at,
                    ContentGeneration.resource,
                    ContentGeneration.adaptation_snapshot,
                ).where(ContentGeneration.id == identifier, ContentGeneration.owner_id == owner)
            )
            .mappings()
            .first()
        )
