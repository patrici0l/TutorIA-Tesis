import os
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.base_datos.session import get_engine
from app.configuracion.settings import get_settings
from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.schemas import InstitutionalIdentity
from app.modulos.autenticacion.servicios.logout_service import LogoutService
from app.modulos.autenticacion.servicios.session_service import SessionService

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Requiere PostgreSQL con migraciones"
    ),
]


def test_postgres_institutional_user_and_revocable_session():
    engine = get_engine()
    columns = {column["name"] for column in inspect(engine).get_columns("usuarios")}
    assert "password" not in columns and "password_hash" not in columns
    unique = uuid4().hex
    # Los commits del servicio liberan savepoints; la transacción exterior se revierte.
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(
                connection, join_transaction_mode="create_savepoint", expire_on_commit=False
            ) as db:
                repository = UserRepository(db)
                service = SessionService(repository, get_settings())
                identity = InstitutionalIdentity(
                    institutional_email=f"test-{unique}@example.org",
                    institutional_id=f"mock:test-{unique}",
                    nombre="Prueba",
                    apellido="Temporal",
                    rol="student",
                )
                token = service.create(identity, None)
                user = service.current_user(token)
                assert user.institutional_id == identity.institutional_id
                replacement = service.create(identity, token)
                assert service.current_user(replacement).id == user.id
                with pytest.raises(HTTPException):
                    service.current_user(token)
                LogoutService(repository).logout(replacement)
                with pytest.raises(HTTPException):
                    service.current_user(replacement)
        finally:
            transaction.rollback()
