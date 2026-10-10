from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def claim(self, identifier: UUID, owner: UUID) -> UUID | None:
        now, token = datetime.now(UTC), uuid4()
        result = self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.owner_id == owner,
                Document.deleted_at.is_(None),
                or_(
                    Document.processing_status.in_(["pending", "failed"]),
                    (Document.processing_status == "processing")
                    & (Document.processing_started_at < now - timedelta(minutes=2)),
                ),
            )
            .values(
                processing_status="processing",
                processing_token=token,
                processing_started_at=now,
                processing_error=None,
            )
            .execution_options(synchronize_session=False)
        )
        self.db.commit()
        self.db.expire_all()
        return token if result.rowcount == 1 else None

    def publish(self, identifier: UUID, token: UUID, chunks: list[dict], metadata: dict) -> bool:
        # The conditional UPDATE locks the document until commit. A delete/retry can
        # invalidate the token; an old worker must never replace its successor's chunks.
        result = self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.processing_token == token,
                Document.processing_status == "processing",
                Document.deleted_at.is_(None),
            )
            .values(
                processing_status="processed",
                processing_token=None,
                processed_at=datetime.now(UTC),
                processing_error=None,
                **metadata,
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            self.db.rollback()
            return False
        self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == identifier))
        self.db.add_all([DocumentChunk(document_id=identifier, **chunk) for chunk in chunks])
        self.db.commit()
        self.db.expire_all()
        return True

    def fail(self, identifier: UUID, token: UUID, code: str):
        self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.processing_token == token,
                Document.processing_status == "processing",
                Document.deleted_at.is_(None),
            )
            .values(processing_status="failed", processing_error=code, processing_token=None)
            .execution_options(synchronize_session=False)
        )
        self.db.commit()
        self.db.expire_all()

    def list_for_document(self, identifier: UUID, limit: int, offset: int):
        query = select(DocumentChunk).where(DocumentChunk.document_id == identifier)
        count = self.db.scalar(select(func.count()).select_from(query.subquery()))
        items = self.db.scalars(
            query.order_by(DocumentChunk.position).limit(limit).offset(offset)
        ).all()
        return items, count
