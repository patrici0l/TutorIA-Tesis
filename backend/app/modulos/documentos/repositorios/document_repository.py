# Consulta y persiste metadatos de documentos restringidos a su propietario.
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.servicios.model_spec import EMBEDDING_VERSION, MODEL_ID, MODEL_REVISION


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def owned(self, identifier: UUID, owner: UUID):
        return self.db.scalar(
            select(Document).where(
                Document.id == identifier, Document.owner_id == owner, Document.deleted_at.is_(None)
            )
        )

    def list_owned(self, owner: UUID, limit: int, offset: int, course: str | None = None):
        query = select(Document).where(Document.owner_id == owner, Document.deleted_at.is_(None))
        if course:
            query = query.where(Document.course == course)
        count = self.db.scalar(select(func.count()).select_from(query.subquery()))
        items = self.db.scalars(
            query.order_by(Document.created_at.desc(), Document.id).limit(limit).offset(offset)
        ).all()
        return items, count

    def save(self, document: Document):
        self.db.add(document)
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def set_publication(self, identifier: UUID, owner: UUID, publish: bool):
        try:
            document = self.db.scalar(
                select(Document)
                .where(
                    Document.id == identifier,
                    Document.owner_id == owner,
                    Document.deleted_at.is_(None),
                )
                .with_for_update()
            )
            if document is None:
                raise HTTPException(404, "Documento no encontrado.")
            if publish:
                if not (
                    document.course
                    and document.source_reference
                    and document.permission_note
                    and document.permission_recorded_at
                    and document.status == "uploaded"
                    and document.processing_status == "processed"
                    and document.index_status == "indexed"
                    and document.embedding_model == MODEL_ID
                    and document.embedding_revision == MODEL_REVISION
                    and document.embedding_version == EMBEDDING_VERSION
                    and document.chunk_count > 0
                ):
                    raise HTTPException(
                        409, "Revisa el permiso, procesa e indexa el material antes de habilitarlo."
                    )
                if document.published_at is None:
                    indexed = self.db.scalar(
                        select(func.count())
                        .select_from(DocumentChunk)
                        .where(
                            DocumentChunk.document_id == identifier,
                            DocumentChunk.embedding.is_not(None),
                        )
                    )
                    if indexed != document.chunk_count:
                        raise HTTPException(
                            409, "El índice está incompleto. Vuelve a indexar el material."
                        )
                    document.published_at = datetime.now(UTC)
            else:
                document.published_at = None
            self.db.commit()
            return document
        except Exception:
            self.db.rollback()
            raise

    def delete_owned(self, identifier: UUID, owner: UUID) -> bool:
        result = self.db.execute(
            update(Document)
            .where(
                Document.id == identifier, Document.owner_id == owner, Document.deleted_at.is_(None)
            )
            .values(
                deleted_at=datetime.now(UTC),
                status="deleted",
                processing_token=None,
                index_token=None,
                chunk_count=0,
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            self.db.rollback()
            return False
        self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == identifier))
        self.db.commit()
        self.db.expire_all()
        return True

    def has_next_version(self, identifier: UUID):
        # Deleted successors still belong to history; never reuse their version number.
        return self.db.scalar(select(Document.id).where(Document.previous_version_id == identifier))

    def search_text(self, owner: UUID, course: str, text: str, limit: int, offset: int):
        query = (
            select(Document, DocumentChunk)
            .join(DocumentChunk, DocumentChunk.document_id == Document.id)
            .where(
                Document.owner_id == owner,
                Document.course == course,
                Document.deleted_at.is_(None),
                Document.processing_status == "processed",
                Document.permission_recorded_at.is_not(None),
                DocumentChunk.text.icontains(text, autoescape=True),
            )
        )
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        rows = self.db.execute(
            query.order_by(Document.id, DocumentChunk.position).limit(limit).offset(offset)
        )
        return rows.all(), total
