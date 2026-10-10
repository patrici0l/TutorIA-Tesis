from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.servicios.model_spec import EMBEDDING_VERSION, MODEL_ID, MODEL_REVISION


class IndexRepository:
    def __init__(self, db: Session):
        self.db = db

    def claim(self, identifier: UUID, owner: UUID, rebuild: bool = False):
        token, now = uuid4(), datetime.now(UTC)
        result = self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.owner_id == owner,
                Document.deleted_at.is_(None),
                Document.processing_status == "processed",
                or_(
                    Document.index_status.in_(
                        ["pending", "failed", "indexed"] if rebuild else ["pending", "failed"]
                    ),
                    (Document.index_status == "indexing")
                    & (Document.index_started_at < now - timedelta(minutes=5)),
                ),
            )
            .values(
                index_status="indexing", index_token=token, index_started_at=now, index_error=None
            )
            .execution_options(synchronize_session=False)
        )
        self.db.commit()
        self.db.expire_all()
        return token if result.rowcount == 1 else None

    def snapshot(self, identifier: UUID):
        rows = self.db.execute(
            select(DocumentChunk.id, DocumentChunk.text)
            .where(DocumentChunk.document_id == identifier)
            .order_by(DocumentChunk.position)
        ).all()
        snapshot = [(row.id, row.text) for row in rows]
        self.db.commit()
        return snapshot

    def publish(self, identifier: UUID, token: UUID, rows: list[dict]):
        result = self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.index_token == token,
                Document.index_status == "indexing",
                Document.deleted_at.is_(None),
                Document.processing_status == "processed",
            )
            .values(
                index_status="indexed",
                index_token=None,
                index_error=None,
                indexed_at=datetime.now(UTC),
                embedding_model=MODEL_ID,
                embedding_revision=MODEL_REVISION,
                embedding_version=EMBEDDING_VERSION,
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            self.db.rollback()
            return False
        current = self.db.scalars(
            select(DocumentChunk.id).where(DocumentChunk.document_id == identifier)
        ).all()
        if set(current) != {row["id"] for row in rows} or len(current) != len(rows):
            self.db.rollback()
            return False
        self.db.bulk_update_mappings(DocumentChunk, rows)
        self.db.commit()
        self.db.expire_all()
        return True

    def fail(self, identifier: UUID, token: UUID, code: str):
        self.db.execute(
            update(Document)
            .where(
                Document.id == identifier,
                Document.index_token == token,
                Document.index_status == "indexing",
                Document.deleted_at.is_(None),
            )
            .values(index_status="failed", index_token=None, index_error=code)
            .execution_options(synchronize_session=False)
        )
        self.db.commit()
        self.db.expire_all()
