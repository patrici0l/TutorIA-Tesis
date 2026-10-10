from typing import get_args
from uuid import UUID

from fastapi import HTTPException

from app.modulos.contenidos.history_schemas import (
    GenerationAudit,
    HistoryDetail,
    HistoryPage,
    RetrievalAudit,
)
from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.repositorios.history_repository import HistoryRepository
from app.modulos.contenidos.servicios.generation_trace_service import CONTENT_ERRORS
from app.modulos.proveedores_ia.errors import ErrorCode


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
                adaptation=row.get("adaptation_snapshot"),
            ),
            status=row["status"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
            resource=row["resource"],
            audit=GenerationAudit(
                generation_started_at=row["generation_started_at"],
                provider=row["provider"],
                requested_model=row["requested_model"],
                model_version=row["model_version"],
                prompt_version=row["prompt_version"],
                prompt_sha256=row["prompt_sha256"],
                usage=row["usage"],
                latency_ms=row["latency_ms"],
                estimated_cost=row["estimated_cost"],
                cost_basis=row.get("cost_basis"),
                error_code=row["error_code"]
                if row["error_code"] in CONTENT_ERRORS | set(get_args(ErrorCode))
                else None,
                retrieval=RetrievalAudit(
                    **{
                        field: row["retrieval_snapshot"][field]
                        for field in RetrievalAudit.model_fields
                    }
                ),
            ),
            message="La generación terminó sin un recurso válido. No se reintentó."
            if row["status"] == "failed"
            else None,
        )
