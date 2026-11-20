# Compone la API y valida configuración antes de aceptar solicitudes.
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.health_router import router
from app.base_datos.session import get_engine
from app.configuracion.constants import API_PREFIX, APP_VERSION
from app.configuracion.logging_config import configure_logging
from app.configuracion.settings import get_settings
from app.modulos.actividades.router import router as assignment_router
from app.modulos.autenticacion.router import router as auth_router
from app.modulos.contenidos.router import router as content_router
from app.modulos.contenidos.rules_router import router as rules_router
from app.modulos.documentos.router import router as documents_router
from app.modulos.integracion_adaptia.router import router as adaptia_router
from app.modulos.metricas.router import router as metrics_router
from app.modulos.perfiles.router import router as profiles_router
from app.modulos.practica.router import router as practice_router
from app.modulos.rag.router import router as rag_router
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter
from app.nucleo.seguridad.upload_limit import UploadLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    get_settings().validate_auth()
    get_settings().validate_llm()
    get_settings().validate_adaptia()
    yield
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()


def create_app() -> FastAPI:
    app = FastAPI(
        title="TutorIA — Integración ADAPTIA",
        description=(
            "Contrato de servicio para que ADAPTIA solicite contenido educativo a TutorIA.\n\n"
            "### Probar la integración\n"
            "1. Pulsa **Authorize** e introduce solo el token de servicio en "
            "**ADAPTIABearer**. Swagger añade `Authorization: Bearer …`.\n"
            "2. Abre **POST /api/v1/tutoria/generate-content** y pulsa **Try it out**.\n"
            "3. Asigna un `X-Request-ID` único y utiliza el perfil sintético de ejemplo. "
            "Conserva ese ID si reintentas exactamente el mismo cuerpo.\n"
            "4. Pulsa **Execute** y revisa `success`, `data`, `metadata` y `tracking`.\n\n"
            "### Resultado esperado\n"
            "Con proveedor habilitado: **200**, texto con explicación, ejemplo y ejercicio. "
            "Con el LLM apagado: **503 / AI_SERVICE_UNAVAILABLE**; no es una generación exitosa. "
            "Token ausente o incorrecto: **401**. Campos inválidos: **422**.\n\n"
            "La dificultad de **1 a 10** la decide ADAPTIA. Esta versión genera texto directo; "
            "la modalidad orienta su presentación. La generación comparte cuota con la web. "
            "Un éxito repetido con el mismo ID y cuerpo devuelve el resultado guardado "
            "sin llamar otra vez al proveedor."
        ),
        version=APP_VERSION,
        servers=[{"url": "/", "description": "Este servidor"}],
        openapi_tags=[
            {
                "name": "Integración ADAPTIA",
                "description": "Perfil y contexto → contenido estructurado y trazabilidad.",
            },
        ],
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "persistAuthorization": False,
        },
        lifespan=lifespan,
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.include_router(router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(rules_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(auth_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(documents_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(rag_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(content_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(profiles_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(metrics_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(practice_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(assignment_router, prefix=API_PREFIX, include_in_schema=False)
    app.include_router(adaptia_router, prefix=API_PREFIX)
    app.add_middleware(UploadLimitMiddleware)
    limiter = AuthRateLimiter()

    @app.middleware("http")
    async def safe_request(request: Request, call_next):
        if request.url.path == f"{API_PREFIX}/auth/login":
            client = request.client.host if request.client else "unknown"
            if not limiter.allow(client):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Demasiados intentos."},
                    headers={"Retry-After": "60", "Cache-Control": "no-store"},
                )
        try:
            response = await call_next(request)
        except Exception:
            logging.getLogger(__name__).error("Request failed; sensitive details omitted")
            if request.url.path == f"{API_PREFIX}/tutoria/generate-content":
                from app.modulos.integracion_adaptia.errors import (
                    IntegrationError,
                    failure_response,
                    request_context,
                )

                return failure_response(request_context(request.headers), IntegrationError(
                    500, "INTERNAL_SERVER_ERROR", "No se pudo completar la solicitud."
                ))
            response = JSONResponse(
                status_code=500, content={"detail": "No se pudo completar la solicitud."}
            )
        if request.url.path.startswith(f"{API_PREFIX}/auth"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith(
            (
                f"{API_PREFIX}/documents",
                f"{API_PREFIX}/rag",
                f"{API_PREFIX}/content",
                f"{API_PREFIX}/profiles",
                f"{API_PREFIX}/metrics",
                f"{API_PREFIX}/practice",
                f"{API_PREFIX}/adaptation",
                f"{API_PREFIX}/tutoria",
            )
        ):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
                    for error in exc.errors()
                ]
            },
        )

    return app


app = create_app()
