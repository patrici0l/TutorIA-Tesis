import io
import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.datastructures import Headers

from app.base_datos.session import get_engine
from app.configuracion.settings import get_settings
from app.modulos.documentos.repositorios.document_repository import DocumentRepository
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.usuarios.models import User

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Requiere PostgreSQL con migraciones"
    ),
]


def test_postgres_document_lifecycle(tmp_path):
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                connection, join_transaction_mode="create_savepoint", expire_on_commit=False
            ) as db:
                owner = User(
                    institutional_email=f"doc-{uuid4().hex}@example.org",
                    nombre="Docente",
                    apellido="Temporal",
                    rol="teacher",
                    activo=True,
                    last_login=datetime.now(UTC),
                )
                db.add(owner)
                db.flush()
                settings = get_settings().model_copy(update={"document_storage_path": tmp_path})
                repository = DocumentRepository(db)
                service = DocumentService(repository, settings)
                file = UploadFile(
                    io.BytesIO(b"Derivadas: corpus sintetico."),
                    filename="derivadas.txt",
                    headers=Headers({"content-type": "text/plain"}),
                )
                record = service.upload(file, "Derivadas", owner.id)
                assert repository.list_owned(owner.id, 20, 0)[1] == 1
                assert service.get(record.id, owner.id).sha256 == record.sha256
                assert (tmp_path / str(record.id)).exists()
                service.delete(record.id, owner.id)
                assert repository.list_owned(owner.id, 20, 0)[1] == 0
                assert not (tmp_path / str(record.id)).exists()
        finally:
            transaction.rollback()
