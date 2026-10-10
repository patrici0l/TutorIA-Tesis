from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.documentos.router import Owner
from app.modulos.rag.repositorios.search_repository import SearchRepository
from app.modulos.rag.schemas import SearchRequest, SearchResponse
from app.modulos.rag.servicios.embedding_worker_client import EmbeddingWorkerClient
from app.modulos.rag.servicios.search_service import SearchService
from app.nucleo.dependencias.auth import require_client_header

router = APIRouter(prefix="/rag", tags=["rag"])


def get_search_service(db: Annotated[Session, Depends(get_session)]):
    return SearchService(SearchRepository(db), EmbeddingWorkerClient(get_settings()))


@router.post(
    "/search", response_model=SearchResponse, dependencies=[Depends(require_client_header)]
)
def search(
    request: SearchRequest,
    user: Owner,
    service: Annotated[SearchService, Depends(get_search_service)],
):
    return service.search(request, user.id)
