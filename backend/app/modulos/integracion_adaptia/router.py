from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import Settings, get_settings
from app.modulos.integracion_adaptia.auth import require_adaptia_token
from app.modulos.integracion_adaptia.errors import (
    CORRELATION,
    IntegrationError,
    failure_response,
    request_context,
)
from app.modulos.integracion_adaptia.repository import AdaptiaRepository
from app.modulos.integracion_adaptia.schemas import (
    AdaptiaFailure,
    AdaptiaGenerationRequest,
    AdaptiaSuccess,
)
from app.modulos.integracion_adaptia.service import AdaptiaService

EXAMPLE = {
    "student_id": "stud_hash_abc123xyz",
    "topic": "derivadas",
    "difficulty": 5,
    "preferred_modality": "visual",
    "context": "Explicar la derivada como tasa de cambio con un ejemplo guiado.",
    "performance_history": [
        {"topic": "regla de la potencia", "score": 60, "time": "2026-11-19T10:00:00Z"}
    ],
    "known_concepts": ["funciones"],
    "gaps": ["regla de la potencia"],
}


class AdaptiaRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            context = request_context(request.headers)
            request.state.adaptia_context = context
            try:
                for name in ("x-request-id", "x-session-id"):
                    values = request.headers.getlist(name)
                    if len(values) > 1 or (values and not CORRELATION.fullmatch(values[0])):
                        raise IntegrationError(400, "INVALID_REQUEST", "Correlación no válida.")
                response = await original(request)
                response.headers["X-Request-ID"] = context.request_id
                response.headers["Cache-Control"] = "no-store"
                return response
            except IntegrationError as error:
                return failure_response(context, error)
            except RequestValidationError as error:
                fields = sorted(
                    {
                        str(item["loc"][1])
                        for item in error.errors()
                        if len(item["loc"]) > 1
                        and item["loc"][1] in AdaptiaGenerationRequest.model_fields
                    }
                )
                return failure_response(
                    context,
                    IntegrationError(
                        422,
                        "INVALID_REQUEST",
                        "Revisa los campos de la solicitud.",
                        details={"fields": fields},
                    ),
                )
            except HTTPException as error:
                return failure_response(
                    context,
                    IntegrationError(
                        error.status_code,
                        "INVALID_REQUEST",
                        "La solicitud no pudo procesarse.",
                        headers=error.headers,
                    ),
                )
            except SQLAlchemyError:
                return failure_response(
                    context,
                    IntegrationError(
                        503, "AI_SERVICE_UNAVAILABLE", "No se pudo acceder a la trazabilidad."
                    ),
                )
            except Exception:
                return failure_response(
                    context,
                    IntegrationError(
                        500, "INTERNAL_SERVER_ERROR", "No se pudo completar la solicitud."
                    ),
                )

        return handler


router = APIRouter(prefix="/tutoria", tags=["Integración ADAPTIA"], route_class=AdaptiaRoute)


def get_adaptia_service(
    db: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return AdaptiaService(AdaptiaRepository(db), settings)


@router.post(
    "/generate-content",
    response_model=AdaptiaSuccess,
    dependencies=[Depends(require_adaptia_token)],
    responses={
        code: {"model": AdaptiaFailure} for code in (400, 401, 409, 413, 422, 429, 500, 502, 503)
    },
    summary="Generar contenido educativo desde el perfil y contexto de ADAPTIA",
    description=(
        "Acceso de servicio con Authorize / ADAPTIABearer. Sin cookie ni x-prototipo-client. "
        "Envía X-Request-ID para idempotencia y correlación; si lo omites se genera uno. "
        "Un éxito repetido con el mismo ID/cuerpo devuelve el resultado guardado, "
        "sin nueva llamada. Un ID en curso, fallido o con otro cuerpo devuelve 409. "
        "X-Session-ID es opcional. Modo directo de texto, sin RAG, imágenes ni audio; "
        "se conserva la dificultad de 1 a 10 decidida por ADAPTIA. "
        "Respeta el presupuesto compartido con la web. Requiere habilitar integración, "
        "token, proveedor, modelo y presupuesto. No habilita gasto por sí mismo."
    ),
)
def generate_content(
    request: Request,
    service: Annotated[AdaptiaService, Depends(get_adaptia_service)],
    payload: Annotated[
        AdaptiaGenerationRequest,
        Body(
            openapi_examples={
                "perfil_sintetico": {"summary": "Perfil sintético de ejemplo", "value": EXAMPLE}
            }
        ),
    ],
    request_id: Annotated[
        str | None,
        Header(
            alias="X-Request-ID",
            max_length=128,
            description="ID ASCII de correlación/idempotencia; conservar al reintentar.",
        ),
    ] = None,
    session_id: Annotated[
        str | None,
        Header(
            alias="X-Session-ID",
            max_length=128,
            description="Correlación opcional de sesión ADAPTIA.",
        ),
    ] = None,
):
    return service.generate(payload, request.state.adaptia_context)
