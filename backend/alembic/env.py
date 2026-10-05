from sqlalchemy import create_engine, pool

from alembic import context
from app.configuracion.settings import get_settings


def run_migrations_offline():
    context.configure(url=get_settings().get_database_url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(get_settings().get_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
