from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document


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
