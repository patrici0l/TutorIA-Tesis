# Recupera vectores compatibles solo del corpus disponible del propietario.
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.servicios.model_spec import EMBEDDING_VERSION, MODEL_ID, MODEL_REVISION


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def eligibility(owner: UUID, course: str):
        return (
            Document.owner_id == owner,
            Document.course == course,
            Document.published_at.is_not(None),
            Document.permission_recorded_at.is_not(None),
            Document.permission_note.is_not(None),
            Document.source_reference.is_not(None),
            Document.deleted_at.is_(None),
            Document.status == "uploaded",
            Document.processing_status == "processed",
            Document.index_status == "indexed",
            Document.embedding_model == MODEL_ID,
            Document.embedding_revision == MODEL_REVISION,
            Document.embedding_version == EMBEDDING_VERSION,
            DocumentChunk.embedding.is_not(None),
        )

    def count_available(self, owner: UUID, course: str):
        count = self.db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .join(Document)
            .where(*self.eligibility(owner, course))
        )
        self.db.commit()  # Do not hold a read transaction during model inference.
        return count

    def statement(
        self, owner: UUID, vector: list[float], top_k: int, course: str, exact: bool = True
    ):
        columns = (
            DocumentChunk.id,
            DocumentChunk.position,
            DocumentChunk.source_kind,
            DocumentChunk.source_index,
            DocumentChunk.char_start,
            DocumentChunk.char_end,
            DocumentChunk.text,
            DocumentChunk.source_sha256,
            DocumentChunk.embedding,
            Document.id.label("document_id"),
            Document.title.label("document_title"),
            Document.filename,
            Document.sha256.label("document_sha256"),
            Document.processing_version,
            Document.course,
            Document.version_number,
            Document.source_reference,
            Document.published_at,
            Document.external_source,
        )
        eligible = select(*columns).join(Document).where(*self.eligibility(owner, course))
        if exact:
            # Filter before ranking; materialization prevents an approximate HNSW scan.
            corpus = eligible.cte("eligible_corpus").prefix_with("MATERIALIZED")
            distance = corpus.c.embedding.cosine_distance(vector)
            return (
                select(corpus, distance.label("distance"))
                .order_by(distance, corpus.c.id)
                .limit(top_k)
            )
        # Used only for controlled evaluation, never selected by API clients.
        distance = DocumentChunk.embedding.cosine_distance(vector)
        return eligible.add_columns(distance.label("distance")).order_by(distance).limit(top_k)

    def search(
        self, owner: UUID, vector: list[float], top_k: int, min_similarity: float, course: str
    ):
        rows = self.db.execute(self.statement(owner, vector, top_k, course)).mappings().all()
        results = []
        for row in rows:
            item = dict(row)
            item.pop("embedding")
            similarity = max(-1.0, min(1.0, 1 - float(item.pop("distance"))))
            if similarity >= min_similarity:
                results.append({**item, "similarity": similarity})
        return results
