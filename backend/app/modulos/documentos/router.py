# Expone gestión de documentos propios con sesión, rol y protección de escritura.
import hashlib
import unicodedata
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.schemas import (
    DocumentList,
    DocumentMetadata,
    DocumentResponse,
    TextMatch,
    TextSearchPage,
)
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.rag.repositorios.chunk_repository import ChunkRepository
from app.modulos.rag.repositorios.index_repository import IndexRepository
from app.modulos.rag.schemas import DocumentChunkList
from app.modulos.rag.servicios.index_document_service import IndexDocumentService
from app.modulos.rag.servicios.ingest_document_service import IngestDocumentService
from app.nucleo.dependencias.auth import require_client_header
from app.nucleo.dependencias.autorizacion import Owner

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_service(db: Annotated[Session, Depends(get_session)]):
    return DocumentService(DocumentRepository(db), get_settings())


def get_ingest_service(db: Annotated[Session, Depends(get_session)]):
    settings = get_settings()
    return IngestDocumentService(
        DocumentService(DocumentRepository(db), settings), ChunkRepository(db), settings
    )


Service = Annotated[DocumentService, Depends(get_document_service)]
IngestService = Annotated[IngestDocumentService, Depends(get_ingest_service)]


def get_index_service(db: Annotated[Session, Depends(get_session)]):
    settings = get_settings()
    return IndexDocumentService(
        DocumentService(DocumentRepository(db), settings), IndexRepository(db), settings
    )


@router.post(
    "/{identifier}/index",
    response_model=DocumentResponse,
    dependencies=[Depends(require_client_header)],
)
def index_document(
    identifier: UUID,
    user: Owner,
    service: Annotated[IndexDocumentService, Depends(get_index_service)],
    rebuild: bool = False,
):
    return service.index(identifier, user.id, rebuild)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
    dependencies=[Depends(require_client_header)],
)
def upload(
    service: Service,
    user: Owner,
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form(min_length=1, max_length=160)],
    course: Annotated[str, Form(min_length=1, max_length=160)],
    source_reference: Annotated[str, Form(min_length=1, max_length=500)],
    permission_note: Annotated[str, Form(min_length=1, max_length=500)],
    authorization_confirmed: Annotated[bool, Form()],
    previous_version_id: Annotated[UUID | None, Form()] = None,
):
    try:
        if not authorization_confirmed:
            raise HTTPException(422, "Confirma el permiso de uso del material.")
        try:
            metadata = DocumentMetadata(
                course=course,
                source_reference=source_reference,
                permission_note=permission_note,
                previous_version_id=previous_version_id,
            )
        except ValidationError:
            raise HTTPException(422, "Revisa asignatura, procedencia y permiso de uso.") from None
        return service.upload(file, title, user.id, metadata)
    finally:
        file.file.close()


@router.get("", response_model=DocumentList)
def list_documents(
    service: Service,
    user: Owner,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    course: Annotated[str | None, Query(min_length=1, max_length=160)] = None,
):
    items, total = service.repository.list_owned(
        user.id, limit, offset, normalize_course(course) if course else None
    )
    return DocumentList(items=items, total=total, limit=limit, offset=offset)


def normalize_course(value: str):
    return unicodedata.normalize("NFC", value.strip()).casefold()


@router.get("/text-search", response_model=TextSearchPage)
def text_search(
    service: Service,
    user: Owner,
    course: Annotated[str, Query(min_length=1, max_length=160)],
    q: Annotated[str, Query(min_length=1, max_length=200)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    if not course.strip() or not q.strip():
        raise HTTPException(422, "Indica asignatura y texto de búsqueda.")
    rows, total = service.repository.search_text(
        user.id, normalize_course(course), unicodedata.normalize("NFC", q.strip()), limit, offset
    )
    return TextSearchPage(
        items=[TextMatch(document=d, chunk=c) for d, c in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{identifier}/original")
def original_document(identifier: UUID, service: Service, user: Owner):
    document = service.get(identifier, user.id)
    path = service.settings.document_storage_path.resolve() / str(document.id)
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != document.sha256:
        raise HTTPException(409, "El original no está disponible o su integridad cambió.")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=document.filename,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.get("/{identifier}", response_model=DocumentResponse)
def get_document(identifier: UUID, service: Service, user: Owner):
    return service.get(identifier, user.id)


@router.delete("/{identifier}", status_code=204, dependencies=[Depends(require_client_header)])
def delete_document(identifier: UUID, service: Service, user: Owner):
    service.delete(identifier, user.id)


@router.post(
    "/{identifier}/process",
    response_model=DocumentResponse,
    dependencies=[Depends(require_client_header)],
)
def process_document(identifier: UUID, service: IngestService, user: Owner):
    return service.process(identifier, user.id)


@router.get("/{identifier}/chunks", response_model=DocumentChunkList)
def list_chunks(
    identifier: UUID,
    service: IngestService,
    user: Owner,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    service.documents.get(identifier, user.id)
    items, total = service.repository.list_for_document(identifier, limit, offset)
    return DocumentChunkList(items=items, total=total, limit=limit, offset=offset)
