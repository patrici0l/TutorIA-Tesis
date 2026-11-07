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
