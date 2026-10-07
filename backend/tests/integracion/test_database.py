import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.base_datos.session import get_engine
from app.main import create_app

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1", reason="Definir RUN_DB_TESTS=1 con PostgreSQL disponible"
    ),
]


def test_real_database_and_vector():
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").status_code == 200
        with get_engine().connect() as connection:
            distance = connection.execute(text("SELECT '[1,2]'::vector <-> '[1,2]'::vector"))
            assert distance.scalar_one() == 0
            revision = connection.execute(text("SELECT version_num FROM alembic_version"))
            assert revision.scalar_one() == "0007_generation_claim"
