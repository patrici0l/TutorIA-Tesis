import hashlib
from types import SimpleNamespace
from uuid import UUID, uuid4

import numpy as np
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_documents import HEADERS, upload
from test_documents import document_app as document_app

from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.servicios.embedding_service import (
    EmbeddingError,
    EmbeddingService,
    normalize_pool,
)
from app.modulos.rag.servicios.index_document_service import IndexDocumentService, validated_vectors
from app.modulos.rag.servicios.prepare_model import verified
from app.nucleo.dependencias.auth import get_current_user


def test_masked_mean_and_unit_normalization():
    hidden = np.array([[[3.0, 4.0], [3.0, 4.0], [999.0, 999.0]]])
    result = normalize_pool(hidden, np.array([[1, 1, 0]]))
    np.testing.assert_allclose(result, [[0.6, 0.8]], atol=1e-7)
    with pytest.raises(EmbeddingError):
        normalize_pool(np.zeros((1, 2, 384)), np.array([[1, 1]]))


def test_encoder_prefixes_and_rejects_overflow_without_inference():
    service = object.__new__(EmbeddingService)
    seen = []

    def encode(text):
        seen.append(text)
        return SimpleNamespace(ids=list(range(513)), attention_mask=[1] * 513)

    service.tokenizer = SimpleNamespace(encode=encode)
    service.session = SimpleNamespace(get_inputs=lambda: [])
    for kind in ("query", "passage"):
        with pytest.raises(EmbeddingError, match="token_limit"):
            service.encode(["Derivada"], kind)
        assert seen[-1] == f"{kind}: Derivada"


def test_public_artifact_checksum(tmp_path):
    path = tmp_path / "model"
    path.write_bytes(b"synthetic weights")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert verified(path, 17, digest)
    path.write_bytes(b"altered weights!!")
    assert not verified(path, 17, digest)


@pytest.mark.parametrize(
    "vector,count",
    [([0.0] * 384, 10), ([float("nan")] * 384, 10), ([1.0], 10), ([1.0] + [0.0] * 383, 513)],
)
def test_vectors_must_be_complete_finite_normalized(vector, count):
    with pytest.raises(ValueError):
        validated_vectors({"vectors": [vector], "token_counts": [count]}, [(uuid4(), "source")])


def test_index_api_is_owned_csrf_protected_idempotent_and_deleted(document_app, monkeypatch):
    client, engine, app, owner, other, _ = document_app
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"
    assert client.post(f"{url}/index", headers=HEADERS).status_code == 409
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 200
    assert client.post(f"{url}/index").status_code == 403
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.post(f"{url}/index", headers=HEADERS).status_code == 404
    app.dependency_overrides[get_current_user] = lambda: owner
    monkeypatch.setattr(
        IndexDocumentService,
        "embed",
        lambda *args: {
            "vectors": [[1.0] + [0.0] * 383],
            "token_counts": [12],
        },
    )
    result = client.post(f"{url}/index", headers=HEADERS)
    assert result.status_code == 200, result.text
    record = result.json()
    assert record["index_status"] == "indexed" and record["embedding_revision"]
    assert "index_token" not in record
    assert result.headers["Cache-Control"] == "no-store"
    monkeypatch.setattr(
        IndexDocumentService, "embed", lambda *args: pytest.fail("Repeated index must not embed")
    )
    assert client.post(f"{url}/index", headers=HEADERS).json() == record
    with Session(engine) as db:
        row = db.scalar(select(DocumentChunk).where(DocumentChunk.document_id == UUID(identifier)))
        assert len(row.embedding) == 384 and row.embedding_tokens == 12
        chunk_id = row.id
    monkeypatch.setattr(
        IndexDocumentService,
        "embed",
        lambda *args: {
            "vectors": [[0.0, 1.0] + [0.0] * 382],
            "token_counts": [12],
        },
    )
    assert client.post(f"{url}/index?rebuild=true", headers=HEADERS).status_code == 200
    with Session(engine) as db:
        row = db.get(DocumentChunk, chunk_id)
        assert row.id == chunk_id and row.embedding[1] == 1
    assert client.delete(url, headers=HEADERS).status_code == 204
    with Session(engine) as db:
        assert not db.scalars(select(DocumentChunk)).all()


@pytest.mark.parametrize(
    "result,code,status",
    [
        ({"error": "model_unavailable"}, "model_unavailable", 503),
        ({"error": "token_limit"}, "token_limit", 422),
        ({"error": "embedding_timeout"}, "embedding_timeout", 422),
        ({"vectors": [], "token_counts": []}, "invalid_embedding", 422),
    ],
)
def test_failed_index_is_safe_and_does_not_store_partial_vectors(
    document_app, monkeypatch, result, code, status
):
    client, engine, _, _, _, _ = document_app
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"
    client.post(f"{url}/process", headers=HEADERS)
    monkeypatch.setattr(IndexDocumentService, "embed", lambda *args: result)
    assert client.post(f"{url}/index", headers=HEADERS).status_code == status
    assert client.get(url).json()["index_error"] == code
    with Session(engine) as db:
        assert all(chunk.embedding is None for chunk in db.scalars(select(DocumentChunk)).all())
