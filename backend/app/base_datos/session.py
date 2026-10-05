from functools import lru_cache

from sqlalchemy import Engine, create_engine

from app.configuracion.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().get_database_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={"connect_timeout": 3, "options": "-c statement_timeout=3000"},
        hide_parameters=True,
    )
