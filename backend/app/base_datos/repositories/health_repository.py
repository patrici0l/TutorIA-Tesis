from sqlalchemy import Engine, text


class HealthRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def check(self) -> tuple[bool, bool]:
        with self.engine.connect() as connection:
            database_ok = connection.execute(text("SELECT 1")).scalar_one() == 1
            vector_ok = connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            ).scalar_one()
        return database_ok, bool(vector_ok)
