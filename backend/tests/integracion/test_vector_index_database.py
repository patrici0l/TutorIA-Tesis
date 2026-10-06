import os
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest
from sqlalchemy import select, text, update
from test_ingestion_database import postgres_ingestion as postgres_ingestion

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.repositorios.index_repository import IndexRepository
from app.modulos.rag.servicios.embedding_service import EmbeddingError, EmbeddingService
from app.modulos.rag.servicios.index_document_service import IndexDocumentService

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="Requires migrated PostgreSQL"),
]


def test_index_lease_fencing_and_deletion(postgres_ingestion):
    db, owner, document, documents, chunks, ingest, _ = postgres_ingestion
    ingest.process(document.id, owner.id)
    repository = IndexRepository(db)
    first = repository.claim(document.id, owner.id)
    assert first and repository.claim(document.id, owner.id) is None
    db.execute(
        update(Document)
        .where(Document.id == document.id)
        .values(index_started_at=datetime.now(UTC) - timedelta(minutes=6))
    )
    db.commit()
    second = repository.claim(document.id, owner.id)
    snapshot = repository.snapshot(document.id)
    rows = [{"id": snapshot[0][0], "embedding": [1.0] + [0.0] * 383, "embedding_tokens": 10}]
    assert repository.publish(document.id, first, rows) is False
    repository.fail(document.id, first, "embedding_failed")
    assert documents.get(document.id, owner.id).index_token == second
    documents.delete(document.id, owner.id)
    assert repository.publish(document.id, second, rows) is False
    assert chunks.list_for_document(document.id, 10, 0)[1] == 0


@pytest.mark.skipif(
    os.getenv("RUN_MODEL_TESTS") != "1", reason="Requires prepared pinned local model"
)
def test_real_model_pgvector_persistence_retrieval_and_reproduction(
    postgres_ingestion, monkeypatch
):
    db, owner, document, documents, chunks, ingest, _ = postgres_ingestion
    ingest.process(document.id, owner.id)
    service = IndexDocumentService(documents, IndexRepository(db), ingest.settings)
    original = service.embed

    def without_transaction(texts, kind="passage"):
        assert not db.in_transaction()
        return original(texts, kind)

    monkeypatch.setattr(service, "embed", without_transaction)
    record = service.index(document.id, owner.id)
    assert record.index_status == "indexed"
    chunk = chunks.list_for_document(document.id, 10, 0)[0][0]
    assert len(chunk.embedding) == 384 and 1 <= chunk.embedding_tokens <= 512
    assert abs(np.linalg.norm(chunk.embedding) - 1) < 1e-5
    model = EmbeddingService(ingest.settings.embedding_model_path)
    repeated, counts = model.encode([chunk.text])
    np.testing.assert_allclose(repeated[0], chunk.embedding, atol=1e-6)
    assert counts[0] == chunk.embedding_tokens
    passages = [
        "La derivada mide la tasa de cambio instantánea de una función.",
        "El volumen de un cubo es el producto de sus tres dimensiones.",
        "Una base de datos almacena tablas con registros.",
    ]
    vectors, _ = model.encode(passages)
    query, _ = model.encode(["¿Qué representa la tasa de cambio instantánea?"], "query")
    assert int(np.argmax(np.array(vectors) @ np.array(query[0]))) == 0
    distance = DocumentChunk.embedding.cosine_distance(query[0])
    found = db.scalar(
        select(DocumentChunk)
        .join(Document)
        .where(
            Document.owner_id == owner.id,
            Document.deleted_at.is_(None),
            Document.index_status == "indexed",
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(1)
    )
    assert found.id == chunk.id
    assert (
        db.scalar(
            text("SELECT count(*) FROM pg_indexes WHERE indexname='ix_fragmentos_embedding_cosine'")
        )
        == 1
    )
    oversized = "x " * 600
    assert len(model.tokenizer.encode(f"passage: {oversized}").ids) > 512
    with pytest.raises(EmbeddingError, match="token_limit"):
        model.encode([oversized])
    monkeypatch.setattr(service, "embed", lambda *_: pytest.fail("Index must be idempotent"))
    assert service.index(document.id, owner.id).indexed_at == record.indexed_at
