from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.schemas import DocumentList, DocumentResponse
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user, require_client_header

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_owner(user: Annotated[User, Depends(get_current_user)]):
    if user.rol not in {"teacher", "admin"}:
        raise HTTPException(403, "La gestión de documentos requiere permisos de docente.")
    return user


def get_document_service(db: Annotated[Session, Depends(get_session)]):
    return DocumentService(DocumentRepository(db), get_settings())


Owner = Annotated[User, Depends(get_document_owner)]
Service = Annotated[DocumentService, Depends(get_document_service)]


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
):
    try:
        return service.upload(file, title, user.id)
    finally:
        file.file.close()


@router.get("", response_model=DocumentList)
def list_documents(
    service: Service,
    user: Owner,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = service.repository.list_owned(user.id, limit, offset)
    return DocumentList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{identifier}", response_model=DocumentResponse)
def get_document(identifier: UUID, service: Service, user: Owner):
    return service.get(identifier, user.id)


@router.delete("/{identifier}", status_code=204, dependencies=[Depends(require_client_header)])
def delete_document(identifier: UUID, service: Service, user: Owner):
    service.delete(identifier, user.id)
