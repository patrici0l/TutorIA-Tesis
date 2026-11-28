from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import ValidationError

from app.modulos.documentos.core_schemas import CorePreview, CoreResult, CoreSource
from app.modulos.documentos.external_router import Reader, snapshot
from app.modulos.documentos.router import Service
from app.modulos.documentos.schemas import DocumentMetadata, DocumentResponse
from app.modulos.documentos.servicios.core_service import CoreService
from app.nucleo.dependencias.auth import require_client_header

router = APIRouter(prefix="/documents/external/core", tags=["external sources"])


def get_core():
    return CoreService()


Core = Annotated[CoreService, Depends(get_core)]


@router.get("/search", response_model=list[CoreResult])
def search(user: Reader, core: Core, q: Annotated[str, Query(min_length=2, max_length=160)]):
    query = q.strip()
    if len(query) < 2 or any(ord(c) < 32 for c in query):
        raise HTTPException(422, "Escribe un tema de al menos dos caracteres.")
    return core.search(query)


@router.get("/preview/{work_id}", response_model=CorePreview)
def preview(work_id: int, user: Reader, core: Core):
    if work_id <= 0:
        raise HTTPException(422, "Publicación no válida.")
    result, _ = core.preview(work_id)
    return result


@router.post(
    "/import",
    response_model=DocumentResponse,
    status_code=201,
    dependencies=[Depends(require_client_header)],
)
def import_original(
    user: Reader,
    core: Core,
    service: Service,
    file: Annotated[UploadFile, File()],
    work_id: Annotated[int, Form(gt=0)],
    record_sha256: Annotated[str, Form(pattern=r"^[a-f0-9]{64}$")],
    course: Annotated[str, Form(min_length=1, max_length=160)],
    permission_note: Annotated[str, Form(min_length=10, max_length=500)],
    authorization_confirmed: Annotated[bool, Form()],
):
    if not authorization_confirmed:
        raise HTTPException(
            422, "Confirma que el archivo corresponde a la publicación y que puedes utilizarlo."
        )
    result, raw = core.preview(work_id)
    if result.record_sha256 != record_sha256:
        raise HTTPException(409, "La ficha de CORE cambió. Vuelve a revisarla antes de añadirla.")
    source = CoreSource(
        work_id=result.work_id,
        title=result.title,
        url=result.url,
        authors=result.authors,
        year=result.year,
        retrieved_at=result.retrieved_at,
        license_name=result.license_statement,
        attribution="; ".join(result.authors) or "Autores no informados por CORE",
        record_sha256=result.record_sha256,
        snapshot_sha256=result.record_sha256,
    )
    try:
        metadata = DocumentMetadata(
            course=course, source_reference=result.url, permission_note=permission_note
        )
    except ValidationError:
        raise HTTPException(422, "Revisa la asignatura y el permiso de uso.") from None
    # El original aportado conserva sus bytes. El resumen nunca se guarda como artículo.
    return service.upload(
        file,
        result.title[:160],
        user.id,
        metadata,
        external_source=source.model_dump(mode="json"),
        source_snapshot=raw,
    )


router.add_api_route("/snapshot/{identifier}", snapshot, methods=["GET"])
