import hmac
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.configuracion.settings import Settings, get_settings
from app.modulos.integracion_adaptia.errors import IntegrationError

bearer = HTTPBearer(
    auto_error=False,
    scheme_name="ADAPTIABearer",
    description="Token de servicio de ADAPTIA configurado en el backend; no es la cookie docente.",
)


def require_adaptia_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    expected = settings.adaptia_service_token.get_secret_value()
    if not settings.adaptia_enabled or len(expected) < 32:
        raise IntegrationError(503, "AI_SERVICE_UNAVAILABLE", "La integración no está habilitada.")
    if credentials is None or not hmac.compare_digest(
        credentials.credentials.encode(), expected.encode()
    ):
        raise IntegrationError(
            401,
            "AUTHENTICATION_FAILED",
            "Se requiere un token de servicio válido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
