from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
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
    document_storage_path: Path = Path("uploads/documents")
    document_max_bytes: int = Field(default=10_485_760, ge=1024, le=10_485_760)
    extraction_timeout_seconds: int = Field(default=15, ge=5, le=20)
    document_chunk_chars: int = Field(default=1000, ge=300, le=2000)
    document_chunk_overlap: int = Field(default=150, ge=0, le=500)
    embedding_model_path: Path = Path("models/e5-small")
    embedding_timeout_seconds: int = Field(default=180, ge=30, le=180)
    llm_free_tier_confirmed: bool = False
    llm_daily_request_limit: int = Field(default=5, ge=1, le=20)
    llm_enabled: bool = False
    llm_default_provider: Literal["gemini", "openai", "claude"] = "gemini"
    llm_model: str = ""
    gemini_api_key: SecretStr = Field(default=SecretStr(""), repr=False)
    llm_timeout_seconds: int = Field(default=30, ge=5, le=60)
    llm_max_input_chars: int = Field(default=12000, ge=1000, le=24000)
    llm_max_output_tokens: int = Field(default=1024, ge=128, le=4096)
    llm_requests_per_minute: int = Field(default=5, ge=1, le=10)
    auth_mode: Literal["mock", "cas"] = "mock"
    auth_mock_user: Literal["student", "teacher"] = "student"
    auth_cookie_secure: bool = False
    auth_session_hours: int = Field(default=8, ge=1, le=24)
    auth_callback_url: str = "http://localhost:4200/api/v1/auth/callback"
    auth_frontend_url: str = "http://localhost:4200/inicio"
    auth_login_url: str = "http://localhost:4200/login"
    auth_allowed_domains: str = "est.ups.edu.ec"
    cas_login_url: str = ""
    cas_validate_url: str = ""
    cas_service_parameter: str = "service"
    cas_ticket_parameter: str = "ticket"
    cas_email_attribute: str = "email"
    cas_id_attribute: str = "uid"
    cas_first_name_attribute: str = "givenName"
    cas_last_name_attribute: str = "sn"

    @model_validator(mode="after")
    def validate_chunking(self):
        if self.document_chunk_overlap >= self.document_chunk_chars:
            raise ValueError("DOCUMENT_CHUNK_OVERLAP debe ser menor que DOCUMENT_CHUNK_CHARS")
        return self

    def validate_auth(self) -> None:
        origins = {
            (urlsplit(url).scheme, urlsplit(url).netloc)
            for url in (self.auth_callback_url, self.auth_frontend_url, self.auth_login_url)
        }
        if len(origins) != 1:
            raise ValueError("Callback e interfaz deben compartir origen para la cookie")
        if urlsplit(self.auth_callback_url).path != "/api/v1/auth/callback":
            raise ValueError("AUTH_CALLBACK_URL debe apuntar a /api/v1/auth/callback")
        urls = [self.auth_callback_url, self.auth_frontend_url, self.auth_login_url]
        if self.auth_mode == "mock":
            if self.app_env != "development":
                raise ValueError("AUTH_MODE=mock solo está permitido en desarrollo")
        else:
            if not self.auth_cookie_secure:
                raise ValueError("CAS requiere AUTH_COOKIE_SECURE=true")
            urls += [self.cas_login_url, self.cas_validate_url]
        for url in urls:
            parsed = urlsplit(url)
            if (
                not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.fragment
                or parsed.query
                or parsed.scheme not in {"https", "http"}
            ):
                raise ValueError(
                    "Configura URLs absolutas de autenticación sin credenciales ni query"
                )
            if self.auth_mode == "cas" and parsed.scheme != "https":
                raise ValueError("Todas las URLs del modo CAS deben usar HTTPS")
            if self.auth_mode == "mock" and parsed.hostname not in {
                "localhost",
                "127.0.0.1",
                "::1",
            }:
                raise ValueError("El modo mock solo permite redirecciones a loopback")
        if self.cas_service_parameter == self.cas_ticket_parameter:
            raise ValueError("Los parámetros service y ticket deben ser distintos")
        for name in [self.cas_service_parameter, self.cas_ticket_parameter]:
            if not name.replace("_", "").isalnum():
                raise ValueError("Nombre de parámetro CAS no válido")
        domains = set(self.allowed_domains())
        if not domains or not domains.issubset({"est.ups.edu.ec", "ups.edu.ec"}):
            raise ValueError("Configura dominios institucionales UPS explícitos")

    def validate_llm(self) -> None:
        from app.modulos.proveedores_ia.schemas import validate_model

        if not self.llm_enabled:
            return
        if self.llm_default_provider != "gemini":
            raise ValueError("El primer adaptador disponible es Gemini")
        validate_model(self.llm_model)
        key = self.gemini_api_key.get_secret_value()
        if not key or key != key.strip() or any(ord(char) < 33 or ord(char) > 126 for char in key):
            raise ValueError("Configura GEMINI_API_KEY exclusivamente en el backend")

    def allowed_domains(self) -> list[str]:
        return [
            value.strip().lower() for value in self.auth_allowed_domains.split(",") if value.strip()
        ]

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
