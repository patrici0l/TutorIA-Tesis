from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: SecretStr = SecretStr("")
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tutoria"
    db_user: str = "tutoria"
    db_password: SecretStr = SecretStr("")

    def get_database_url(self) -> URL:
        if self.database_url.get_secret_value():
            from sqlalchemy.engine import make_url

            url = make_url(self.database_url.get_secret_value())
            if url.drivername not in {"postgresql", "postgresql+psycopg"}:
                raise ValueError("DATABASE_URL debe usar PostgreSQL con psycopg")
            return url.set(drivername="postgresql+psycopg")
        return URL.create(
            "postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
