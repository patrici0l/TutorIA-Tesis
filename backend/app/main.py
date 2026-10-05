from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.health_router import router
from app.base_datos.session import get_engine
from app.configuracion.constants import API_PREFIX, APP_VERSION
from app.configuracion.logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
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

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "No se pudo completar la solicitud. Inténtalo nuevamente."},
        )

    return app


app = create_app()
