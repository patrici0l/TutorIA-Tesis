import subprocess
from threading import BoundedSemaphore
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_documents import HEADERS, pdf, upload
from test_documents import document_app as document_app

from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.nucleo.dependencias.auth import get_current_user


def test_processing_traceability_pagination_idempotency_and_delete(document_app):
    client, engine, _, _, _, _ = document_app
    text = "La derivada de x² es 2x.\n\nUn segundo párrafo para verificar sus fuentes."
    identifier = upload(client, content=text.encode("utf-8")).json()["id"]
    url = f"/api/v1/documents/{identifier}"
    assert client.get(f"{url}/chunks").json()["total"] == 0
    result = client.post(f"{url}/process", headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.headers["Cache-Control"] == "no-store"
    record = result.json()
    assert record["processing_status"] == "processed"
    assert record["chunk_count"] == 2 and record["processed_at"]
    assert record["processing_version"] == "text-v1"
    assert record["chunk_chars"] == 1000 and record["chunk_overlap"] == 150
    assert record["text_chars"] == sum(len(paragraph) for paragraph in text.split("\n\n"))
    assert "processing_token" not in record
    page = client.get(f"{url}/chunks?limit=1&offset=1").json()
    assert page["total"] == 2 and page["items"][0]["source_index"] == 2
    first_chunks = client.get(f"{url}/chunks").json()["items"]
    assert client.get(f"{url}/chunks").headers["Cache-Control"] == "no-store"
    assert first_chunks[0]["text"] == "La derivada de x² es 2x."
    assert first_chunks[0]["source_kind"] == "paragraph"
    assert first_chunks[0]["char_start"] == 0
    assert first_chunks[0]["char_end"] == len(first_chunks[0]["text"])
    assert client.post(f"{url}/process", headers=HEADERS).json() == record
    assert client.get(f"{url}/chunks").json()["items"] == first_chunks
    assert client.get(f"{url}/chunks?limit=51").status_code == 422
    assert client.delete(url, headers=HEADERS).status_code == 204
    assert client.get(f"{url}/chunks").status_code == 404
    with Session(engine) as db:
        assert not db.scalars(select(DocumentChunk)).all()


def test_processing_permissions_and_csrf(document_app):
    client, _, app, owner, other, _ = document_app
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"
    assert client.post(f"{url}/process").status_code == 403
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 404
    assert client.get(f"{url}/chunks").status_code == 404
    owner.rol = "student"
    app.dependency_overrides[get_current_user] = lambda: owner
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 403
    assert client.get(f"{url}/chunks").status_code == 403
    app.dependency_overrides.pop(get_current_user)
    assert client.get(f"{url}/chunks").status_code == 401


def test_scanned_pdf_has_safe_failed_state_and_can_retry(document_app):
    client, _, _, _, _, _ = document_app
    identifier = upload(client, "curso.pdf", pdf(), "application/pdf").json()["id"]
    url = f"/api/v1/documents/{identifier}"
    for _ in range(2):
        result = client.post(f"{url}/process", headers=HEADERS)
        assert result.status_code == 422 and "OCR" in result.json()["detail"]
        record = client.get(url).json()
        assert record["processing_status"] == "failed"
        assert record["processing_error"] == "empty_text"
        assert record["chunk_count"] == 0 and record["processed_at"] is None
        assert client.get(f"{url}/chunks").json()["items"] == []


@pytest.mark.parametrize("missing", [False, True])
def test_private_file_integrity_and_absence(document_app, missing):
    client, _, _, _, _, directory = document_app
    identifier = upload(client).json()["id"]
    if missing:
        (directory / identifier).unlink()
    else:
        (directory / identifier).write_bytes(b"contenido alterado")
    url = f"/api/v1/documents/{identifier}"
    result = client.post(f"{url}/process", headers=HEADERS)
    assert result.status_code == 422
    assert str(directory) not in result.text
    assert "contenido alterado" not in result.text
    assert client.get(url).json()["processing_error"] == (
        "file_missing" if missing else "file_changed"
    )


def test_timeout_and_failure_do_not_leave_partial_chunks(document_app, monkeypatch):
    client, engine, _, _, _, _ = document_app
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 15
        raise subprocess.TimeoutExpired("private worker", 15)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 422
    assert client.get(url).json()["processing_error"] == "extraction_timeout"
    with Session(engine) as db:
        document = db.get(Document, UUID(identifier))
        assert document.processing_token is None
        assert not db.scalars(select(DocumentChunk)).all()


def test_busy_capacity_does_not_claim_document(document_app, monkeypatch):
    from app.modulos.rag.servicios import ingest_document_service

    client = document_app[0]
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"
    monkeypatch.setattr(ingest_document_service, "EXTRACTION_SLOTS", BoundedSemaphore(0))
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 429
    assert client.get(url).json()["processing_status"] == "pending"


def test_publish_failure_rolls_back_and_is_retryable(document_app, monkeypatch):
    from app.modulos.rag.repositorios.chunk_repository import ChunkRepository

    client, engine, _, _, _, _ = document_app
    identifier = upload(client).json()["id"]
    url = f"/api/v1/documents/{identifier}"

    def fail(*args, **kwargs):
        raise RuntimeError("database diagnostic must remain private")

    with monkeypatch.context() as patch:
        patch.setattr(ChunkRepository, "publish", fail)
        result = client.post(f"{url}/process", headers=HEADERS)
        assert result.status_code == 500 and "diagnostic" not in result.text
    with Session(engine) as db:
        assert not db.scalars(select(DocumentChunk)).all()
    assert client.get(url).json()["processing_status"] == "failed"
    assert client.post(f"{url}/process", headers=HEADERS).status_code == 200


def test_active_claim_returns_conflict(document_app):
    from app.modulos.rag.repositorios.chunk_repository import ChunkRepository

    client, engine, _, owner, _, _ = document_app
    identifier = upload(client).json()["id"]
    with Session(engine) as db:
        assert ChunkRepository(db).claim(UUID(identifier), owner.id)
    assert (
        client.post(f"/api/v1/documents/{identifier}/process", headers=HEADERS).status_code == 409
    )


def test_worker_crash_has_safe_result(document_app, monkeypatch):
    client = document_app[0]
    identifier = upload(client).json()["id"]

    class CrashedWorker:
        returncode = -9
        stdout = b""

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: CrashedWorker())
    result = client.post(f"/api/v1/documents/{identifier}/process", headers=HEADERS)
    assert result.status_code == 422
    assert (
        client.get(f"/api/v1/documents/{identifier}").json()["processing_error"]
        == "extraction_failed"
    )
