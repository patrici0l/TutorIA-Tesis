import hashlib
import io
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import UploadFile
from sqlalchemy import delete, update
from sqlalchemy.orm import Session
from starlette.datastructures import Headers

from app.base_datos.session import get_engine
from app.configuracion.settings import get_settings
from app.modulos.documentos.models import Document
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.rag.repositorios.chunk_repository import ChunkRepository
from app.modulos.rag.servicios.ingest_document_service import IngestDocumentService
from app.modulos.usuarios.models import User

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Requiere PostgreSQL con migraciones"
    ),
]

SOURCE = "Derivada de x²: 2x. Material sintético de prueba."


@pytest.fixture
def postgres_ingestion(tmp_path):
    # Service commits release a SAVEPOINT; the outer transaction is always
    # rolled back, so neither mock accounts nor documents survive these tests.
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                connection, join_transaction_mode="create_savepoint", expire_on_commit=False
            ) as db:
                owner = User(
                    institutional_email=f"ingestion-{uuid4().hex}@example.org",
                    nombre="Docente",
                    apellido="Temporal",
                    rol="teacher",
                    activo=True,
                    last_login=datetime.now(UTC),
                )
                db.add(owner)
                db.flush()
                settings = get_settings().model_copy(update={"document_storage_path": tmp_path})
                documents = DocumentService(DocumentRepository(db), settings)
                chunks = ChunkRepository(db)
                ingest = IngestDocumentService(documents, chunks, settings)
                file = UploadFile(
                    io.BytesIO(SOURCE.encode("utf-8")),
                    filename="derivadas.txt",
                    headers=Headers({"content-type": "text/plain"}),
                )
                try:
                    document = documents.upload(file, "Derivadas sintéticas", owner.id)
                finally:
                    file.file.close()
                yield db, owner, document, documents, chunks, ingest, tmp_path
        finally:
            transaction.rollback()


def publication():
    chunk = {
        "position": 0,
        "source_kind": "paragraph",
        "source_index": 1,
        "char_start": 0,
        "char_end": len(SOURCE),
        "text": SOURCE,
        "source_sha256": hashlib.sha256(SOURCE.encode("utf-8")).hexdigest(),
    }
    metadata = {
        "text_chars": len(SOURCE),
        "chunk_count": 1,
        "processing_version": "fencing-test-v1",
        "chunk_chars": 1000,
        "chunk_overlap": 150,
    }
    return [chunk], metadata


def test_postgres_processing_lease_fences_expired_workers(postgres_ingestion):
    db, owner, document, documents, chunks, _, _ = postgres_ingestion
    first_token = chunks.claim(document.id, owner.id)
    assert first_token is not None
    assert chunks.claim(document.id, owner.id) is None

    db.execute(
        update(Document)
        .where(Document.id == document.id)
        .values(processing_started_at=datetime.now(UTC) - timedelta(minutes=3))
    )
    db.commit()
    second_token = chunks.claim(document.id, owner.id)
    assert second_token is not None and second_token != first_token
    payload, metadata = publication()

    # A late worker cannot publish or mark the newer attempt as failed.
    assert chunks.publish(document.id, first_token, payload, metadata) is False
    chunks.fail(document.id, first_token, "extraction_failed")
    current = documents.get(document.id, owner.id)
    assert current.processing_status == "processing"
    assert current.processing_token == second_token
    assert chunks.list_for_document(document.id, 10, 0)[1] == 0

    assert chunks.publish(document.id, second_token, payload, metadata) is True
    published, count = chunks.list_for_document(document.id, 10, 0)
    assert count == 1 and published[0].text == SOURCE
    published_id = published[0].id
    assert chunks.publish(document.id, first_token, payload, metadata) is False
    chunks.fail(document.id, first_token, "extraction_failed")
    assert documents.get(document.id, owner.id).processing_status == "processed"
    assert chunks.list_for_document(document.id, 10, 0)[0][0].id == published_id


def test_postgres_real_extraction_is_idempotent(postgres_ingestion, monkeypatch):
    _, owner, document, documents, chunks, ingest, _ = postgres_ingestion
    original_extract = ingest.extract

    def extraction_without_open_transaction(request):
        assert not chunks.db.in_transaction()
        return original_extract(request)

    monkeypatch.setattr(ingest, "extract", extraction_without_open_transaction)
    first = ingest.process(document.id, owner.id)
    assert first.processing_status == "processed"
    assert first.chunk_count == 1 and first.text_chars == len(SOURCE)
    assert first.processing_version and first.processed_at
    processed_at = first.processed_at
    published, count = chunks.list_for_document(document.id, 10, 0)
    assert count == 1
    assert published[0].text == SOURCE
    assert published[0].source_kind == "paragraph" and published[0].source_index == 1
    assert published[0].source_sha256 == hashlib.sha256(SOURCE.encode("utf-8")).hexdigest()
    identifier = published[0].id

    def unexpected_extraction(_request):
        pytest.fail("A processed document must retain its existing fragments")

    monkeypatch.setattr(ingest, "extract", unexpected_extraction)
    second = ingest.process(document.id, owner.id)
    assert second.processed_at == processed_at
    assert chunks.list_for_document(document.id, 10, 0)[0][0].id == identifier
    documents.delete(document.id, owner.id)
    assert chunks.list_for_document(document.id, 10, 0)[1] == 0


def test_postgres_delete_invalidates_inflight_publication(postgres_ingestion):
    db, owner, document, documents, chunks, _, directory = postgres_ingestion
    token = chunks.claim(document.id, owner.id)
    assert token is not None
    documents.delete(document.id, owner.id)
    assert not (directory / str(document.id)).exists()
    payload, metadata = publication()
    assert chunks.publish(document.id, token, payload, metadata) is False
    chunks.fail(document.id, token, "extraction_failed")
    assert chunks.claim(document.id, owner.id) is None
    assert chunks.list_for_document(document.id, 10, 0)[1] == 0
    record = db.get(Document, document.id)
    assert record.status == "deleted" and record.deleted_at
    assert record.processing_token is None and record.chunk_count == 0


def test_postgres_concurrent_claim_and_delete_fence(tmp_path):
    engine = get_engine()
    owner_id, document_id = uuid4(), uuid4()
    settings = get_settings().model_copy(update={"document_storage_path": tmp_path})
    try:
        with Session(engine, expire_on_commit=False) as db:
            owner = User(
                id=owner_id,
                institutional_email=f"race-{owner_id.hex}@example.org",
                nombre="Docente",
                apellido="Temporal",
                rol="teacher",
                activo=True,
                last_login=datetime.now(UTC),
            )
            db.add(owner)
            db.flush()
            db.add(
                Document(
                    id=document_id,
                    owner_id=owner_id,
                    filename="race.txt",
                    title="Prueba temporal",
                    mime_type="text/plain",
                    size_bytes=len(SOURCE.encode("utf-8")),
                    sha256=hashlib.sha256(SOURCE.encode("utf-8")).hexdigest(),
                    status="uploaded",
                )
            )
            db.commit()
        barrier = Barrier(2)

        def claim():
            with Session(engine) as db:
                barrier.wait(timeout=10)
                return ChunkRepository(db).claim(document_id, owner_id)

        with ThreadPoolExecutor(max_workers=2) as pool:
            attempts = [pool.submit(claim), pool.submit(claim)]
            tokens = [attempt.result(timeout=15) for attempt in attempts]
        assert sum(token is not None for token in tokens) == 1
        token = next(token for token in tokens if token)
        payload, metadata = publication()
        barrier = Barrier(2)

        def publish():
            with Session(engine) as db:
                barrier.wait(timeout=10)
                return ChunkRepository(db).publish(document_id, token, payload, metadata)

        def remove():
            with Session(engine) as db:
                barrier.wait(timeout=10)
                DocumentService(DocumentRepository(db), settings).delete(document_id, owner_id)

        with ThreadPoolExecutor(max_workers=2) as pool:
            finishing, deleting = pool.submit(publish), pool.submit(remove)
            finishing.result(timeout=15)
            deleting.result(timeout=15)
        with Session(engine) as db:
            record = db.get(Document, document_id)
            assert record.deleted_at and record.processing_token is None
            assert ChunkRepository(db).list_for_document(document_id, 10, 0)[1] == 0
    finally:
        # Only the UUIDs created by this test are removed; real corpus is untouched.
        with Session(engine) as db:
            db.execute(delete(Document).where(Document.id == document_id))
            db.execute(delete(User).where(User.id == owner_id))
            db.commit()
