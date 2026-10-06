import hashlib
import logging
import unicodedata
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile

from app.configuracion.settings import Settings
from app.modulos.documentos.models import Document
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.servicios.document_validation_service import DocumentValidationService


class DocumentService:
    def __init__(self, repository: DocumentRepository, settings: Settings):
        self.repository, self.settings = repository, settings

    def get(self, identifier: UUID, owner: UUID):
        document = self.repository.owned(identifier, owner)
        if not document:
            raise HTTPException(404, "Documento no encontrado.")
        return document

    def upload(self, file: UploadFile, title: str, owner: UUID):
        title = title.strip()
        if (
            not title
            or len(title) > 160
            or any(unicodedata.category(c).startswith("C") for c in title)
        ):
            raise HTTPException(422, "Escribe un título válido de hasta 160 caracteres.")
        payload = file.file.read(self.settings.document_max_bytes + 1)
        if len(payload) > self.settings.document_max_bytes:
            raise HTTPException(413, "El documento supera el límite de tamaño.")
        filename, mime = DocumentValidationService().validate(
            file.filename or "", file.content_type or "", payload
        )
        identifier = uuid4()
        directory = self.settings.document_storage_path.resolve()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / str(identifier)
        document = Document(
            id=identifier,
            owner_id=owner,
            filename=filename,
            title=title,
            mime_type=mime,
            size_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
            status="uploaded",
        )
        try:
            with path.open("xb") as target:
                target.write(payload)
            self.repository.save(document)
        except Exception:
            self.repository.rollback()
            path.unlink(missing_ok=True)
            raise
        return document

    def delete(self, identifier: UUID, owner: UUID):
        if not self.repository.delete_owned(identifier, owner):
            raise HTTPException(404, "Documento no encontrado.")
        try:
            (self.settings.document_storage_path.resolve() / str(identifier)).unlink(
                missing_ok=True
            )
        except OSError:
            logging.getLogger(__name__).warning("Pending private document file cleanup")
