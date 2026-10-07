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
from app.modulos.autenticacion.router import router as auth_router
from app.modulos.contenidos.router import router as content_router
from app.modulos.documentos.router import router as documents_router
from app.modulos.rag.router import router as rag_router
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter
from app.nucleo.seguridad.upload_limit import UploadLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    get_settings().validate_auth()
    get_settings().validate_llm()
    yield
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()


def create_app() -> FastAPI:
    app = FastAPI(
        title="TutorIA-Lucero",
        version=APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{API_PREFIX}/docs",
        redoc_url=f"{API_PREFIX}/redoc",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.include_router(router, prefix=API_PREFIX)
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(documents_router, prefix=API_PREFIX)
    app.include_router(rag_router, prefix=API_PREFIX)
    app.include_router(content_router, prefix=API_PREFIX)
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
            response = JSONResponse(
                status_code=500, content={"detail": "No se pudo completar la solicitud."}
            )
        if request.url.path.startswith(f"{API_PREFIX}/auth"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith(
            (f"{API_PREFIX}/documents", f"{API_PREFIX}/rag", f"{API_PREFIX}/content")
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
