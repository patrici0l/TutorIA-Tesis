from time import perf_counter
from uuid import UUID

from fastapi import HTTPException

from app.modulos.rag.repositorios.search_repository import SearchRepository
from app.modulos.rag.schemas import SearchRequest, SearchResponse
from app.modulos.rag.servicios.embedding_worker_client import EmbeddingWorkerClient
from app.modulos.rag.servicios.index_document_service import validated_vectors
from app.modulos.rag.servicios.model_spec import EMBEDDING_VERSION, MODEL_ID, MODEL_REVISION
from app.modulos.rag.servicios.query_service import QUERY_VERSION, embedding_query

SEARCH_ERRORS = {
    "model_unavailable": (
        503,
        "El modelo local no está preparado o no supera la verificación de integridad.",
    ),
    "embedding_busy": (429, "El modelo local está ocupado. Inténtalo en un momento."),
    "token_limit": (422, "La consulta supera 512 tokens. Escribe una consulta más breve."),
    "embedding_timeout": (503, "La búsqueda tardó demasiado. Puedes reintentarlo."),
}


class SearchService:
    def __init__(self, repository: SearchRepository, worker: EmbeddingWorkerClient):
        self.repository, self.worker = repository, worker

    def search(self, request: SearchRequest, owner: UUID):
        started = perf_counter()
        available = self.repository.count_available(owner)
        expanded = embedding_query(request.query)
        results = []
        if available:
            result = self.worker.encode([expanded], "query")
            if "error" in result:
                status, message = SEARCH_ERRORS.get(
                    result["error"], (503, "No se pudo preparar la consulta. Puedes reintentarlo.")
                )
                raise HTTPException(status, message)
            try:
                vector = validated_vectors(result, [(owner, request.query)])[0]["embedding"]
            except (ValueError, KeyError, TypeError):
                raise HTTPException(
                    503, "El modelo no produjo un vector válido para la consulta."
                ) from None
            results = self.repository.search(owner, vector, request.top_k, request.min_similarity)
        return SearchResponse(
            **request.model_dump(),
            embedding_query=expanded,
            query_version=QUERY_VERSION,
            results=results,
            available_chunks=available,
            embedding_model=MODEL_ID,
            embedding_revision=MODEL_REVISION,
            embedding_version=EMBEDDING_VERSION,
            elapsed_ms=round((perf_counter() - started) * 1000),
        )
