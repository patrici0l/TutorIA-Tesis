from uuid import UUID

from fastapi import HTTPException

from app.modulos.contenidos.history_schemas import HistoryDetail, HistoryPage
from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.repositorios.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, repository: HistoryRepository):
        self.repository = repository

    def page(self, owner: UUID, offset: int, limit: int):
        items, total = self.repository.page(owner, offset, limit)
        return HistoryPage(items=items, total=total, offset=offset, limit=limit)

    def detail(self, identifier: UUID, owner: UUID):
        row = self.repository.detail(identifier, owner)
        if row is None:
            raise HTTPException(404, "Recurso no disponible.")
        request = row["request_snapshot"]
        return HistoryDetail(
            preparation=PreparationResponse(
                id=row["id"],
                topic=request["topic"],
                learning_objective=request["learning_objective"],
                resource_type=request["resource_type"],
                difficulty=request["difficulty"],
                question_count=request.get("question_count"),
                sources=row["sources_snapshot"],
            ),
            status=row["status"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
            resource=row["resource"],
            message="La generación terminó sin un recurso válido. No se reintentó."
            if row["status"] == "failed"
            else None,
        )
