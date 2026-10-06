from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def owned(self, identifier: UUID, owner: UUID):
        return self.db.scalar(
            select(Document).where(
                Document.id == identifier, Document.owner_id == owner, Document.deleted_at.is_(None)
            )
        )

    def list_owned(self, owner: UUID, limit: int, offset: int):
        query = select(Document).where(Document.owner_id == owner, Document.deleted_at.is_(None))
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
