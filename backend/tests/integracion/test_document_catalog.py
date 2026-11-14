"""Catálogo v0.1 sobre PostgreSQL migrado; datos sintéticos y rollback exterior."""

from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import Headers

from app.configuracion.settings import Settings
from app.modulos.documentos.models import Document
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.schemas import DocumentMetadata
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.rag.repositorios.chunk_repository import ChunkRepository
from app.modulos.rag.servicios.ingest_document_service import IngestDocumentService
from tests.integracion.test_content_trace_database import pytestmark, trace_database  # noqa: F401


def test_catalog_postgres_extraction_isolation_and_version_constraint(trace_database, tmp_path):  # noqa: F811
    db, _, owners = trace_database
    settings = Settings(document_storage_path=tmp_path)
    repository = DocumentRepository(db)
    service = DocumentService(repository, settings)
    ingestion = IngestDocumentService(service, ChunkRepository(db), settings)

    def upload(course, previous=None):
        metadata = DocumentMetadata(
            course=course,
            source_reference="Prueba sintética, no material docente",
            permission_note="Generado para prueba técnica local",
            previous_version_id=previous,
        )
        with BytesIO("Derivada y probabilidad: 100% sintético.".encode()) as payload:
            return service.upload(
                UploadFile(
                    payload,
                    filename="sintetico.txt",
                    headers=Headers({"content-type": "text/plain"}),
                ),
                "Prueba v0.1",
                owners[0],
                metadata,
            )

    calculus = upload("Cálculo Diferencial")
    statistics = upload("Probabilidad y Estadística")
    for document in (calculus, statistics):
        assert ingestion.process(document.id, owners[0]).processing_status == "processed"
    rows, total = repository.search_text(owners[0], "cálculo diferencial", "100%", 20, 0)
    assert total == 1 and rows[0][0].id == calculus.id
    assert repository.search_text(owners[1], "cálculo diferencial", "100%", 20, 0)[1] == 0
    assert repository.search_text(owners[0], "cálculo diferencial", "100_", 20, 0)[1] == 0
    successor = upload("Cálculo Diferencial", calculus.id)
    assert successor.version_number == 2
    assert (tmp_path / str(calculus.id)).read_bytes() == (tmp_path / str(successor.id)).read_bytes()
    with pytest.raises(HTTPException) as conflict:
        upload("Cálculo Diferencial", calculus.id)
    assert conflict.value.status_code == 409
    # Verifica la barrera de BD además de la validación previa del servicio.
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(
                Document(
                    owner_id=owners[0],
                    filename="duplicado.txt",
                    title="Duplicado sintético",
                    mime_type="text/plain",
                    size_bytes=1,
                    sha256="0" * 64,
                    previous_version_id=calculus.id,
                    version_number=2,
                )
            )
            db.flush()


def test_gold_filters_course_owner_permission_revision_and_withdrawal(trace_database):  # noqa: F811
    from datetime import UTC, datetime
    from uuid import uuid4

    from app.modulos.rag.models import DocumentChunk
    from app.modulos.rag.repositorios.search_repository import SearchRepository
    from app.modulos.rag.servicios.model_spec import (
        DIMENSIONS,
        EMBEDDING_VERSION,
        MODEL_ID,
        MODEL_REVISION,
    )

    db, _, owners = trace_database
    vector = [1.0] + [0.0] * (DIMENSIONS - 1)
    repo = DocumentRepository(db)
    search = SearchRepository(db)
    documents = []
    for course, owner in [
        ("cálculo diferencial", owners[0]),
        ("probabilidad y estadística", owners[0]),
        ("cálculo diferencial", owners[1]),
    ]:
        document = Document(
            id=uuid4(),
            owner_id=owner,
            filename="sintetico.txt",
            title="Material sintético",
            mime_type="text/plain",
            size_bytes=5,
            sha256="a" * 64,
            course=course,
            source_reference="Prueba sintética",
            permission_note="Permiso de prueba",
            permission_recorded_at=datetime.now(UTC),
            processing_status="processed",
            processing_version="test",
            index_status="indexed",
            chunk_count=1,
            embedding_model=MODEL_ID,
            embedding_revision=MODEL_REVISION,
            embedding_version=EMBEDDING_VERSION,
        )
        db.add(document)
        db.flush()
        db.add(
            DocumentChunk(
                document_id=document.id,
                position=0,
                source_kind="paragraph",
                source_index=1,
                char_start=0,
                char_end=5,
                text="Texto",
                source_sha256="b" * 64,
                embedding=vector,
                embedding_tokens=2,
            )
        )
        db.commit()
        documents.append(document)
    assert search.count_available(owners[0], "cálculo diferencial") == 0
    for document in documents:
        repo.set_publication(document.id, document.owner_id, True)
    hits = search.search(owners[0], vector, 10, 0, "cálculo diferencial")
    assert [hit["document_id"] for hit in hits] == [documents[0].id]
    assert hits[0]["course"] == "cálculo diferencial" and hits[0]["version_number"] == 1
    for field, value in [("permission_recorded_at", None), ("embedding_revision", "vieja")]:
        document = documents[0]
        before = getattr(document, field)
        setattr(document, field, value)
        db.commit()
        assert search.count_available(owners[0], "cálculo diferencial") == 0
        setattr(document, field, before)
        db.commit()
    repo.set_publication(documents[0].id, owners[0], False)
    assert search.search(owners[0], vector, 10, 0, "cálculo diferencial") == []
    assert search.count_available(owners[0], "probabilidad y estadística") == 1
