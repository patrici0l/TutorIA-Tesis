# Coordina archivos privados y metadatos conservando la propiedad del documento.
import hashlib
import logging
import unicodedata
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError

from app.configuracion.settings import Settings
from app.modulos.documentos.models import Document
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.schemas import DocumentMetadata
from app.modulos.documentos.servicios.document_validation_service import DocumentValidationService


class DocumentService:
    def __init__(self, repository: DocumentRepository, settings: Settings):
        self.repository, self.settings = repository, settings

    def get(self, identifier: UUID, owner: UUID):
        document = self.repository.owned(identifier, owner)
        if not document:
            raise HTTPException(404, "Documento no encontrado.")
        return document

    def upload(
        self, file: UploadFile, title: str, owner: UUID, metadata: DocumentMetadata | None = None,
        *, external_source: dict | None = None, source_snapshot: bytes | None = None
    ):
        title = title.strip()
        if (
            not title
            or len(title) > 160
            or any(unicodedata.category(c).startswith("C") for c in title)
        ):
            raise HTTPException(422, "Escribe un título válido de hasta 160 caracteres.")
        previous = None
        if metadata and metadata.previous_version_id:
            previous = self.get(metadata.previous_version_id, owner)
            if previous.course and previous.course != metadata.course:
                raise HTTPException(409, "Una nueva versión debe conservar la asignatura.")
            if self.repository.has_next_version(previous.id):
                raise HTTPException(
                    409, "Ya existe una versión posterior; parte de la última versión."
                )
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
            external_source=external_source,
            id=identifier,
            owner_id=owner,
            filename=filename,
            title=title,
            mime_type=mime,
            size_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
            status="uploaded",
            course=metadata.course if metadata else None,
            source_reference=metadata.source_reference if metadata else None,
            permission_note=metadata.permission_note if metadata else None,
            permission_recorded_at=datetime.now(UTC) if metadata else None,
            previous_version_id=previous.id if previous else None,
            version_number=previous.version_number + 1 if previous else 1,
        )
        try:
            with path.open("xb") as target:
                target.write(payload)
            if source_snapshot is not None:
                path.with_suffix(".source.json").write_bytes(source_snapshot)
            self.repository.save(document)
        except IntegrityError:
            self.repository.rollback()
            path.unlink(missing_ok=True)
            path.with_suffix(".source.json").unlink(missing_ok=True)
            raise HTTPException(409, "Conflicto de versión; actualiza la biblioteca.") from None
        except Exception:
            self.repository.rollback()
            path.unlink(missing_ok=True)
            path.with_suffix(".source.json").unlink(missing_ok=True)
            raise
        return document

    def delete(self, identifier: UUID, owner: UUID):
        if not self.repository.delete_owned(identifier, owner):
            raise HTTPException(404, "Documento no encontrado.")
        try:
            (self.settings.document_storage_path.resolve() / str(identifier)).unlink(
                missing_ok=True
            )
            (self.settings.document_storage_path.resolve() / f"{identifier}.source.json").unlink(
                missing_ok=True
            )
        except OSError:
            logging.getLogger(__name__).warning("Pending private document file cleanup")
