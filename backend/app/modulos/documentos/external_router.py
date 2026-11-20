"""Search, review and explicitly import external articles as unpublished documents."""
import hashlib
import io
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from starlette.datastructures import Headers

from app.modulos.documentos.external_schemas import WikiImport, WikiPreview, WikiResult
from app.modulos.documentos.router import Service
from app.modulos.documentos.schemas import DocumentMetadata, DocumentResponse
from app.modulos.documentos.servicios.mediawiki_service import MediaWikiService
from app.nucleo.dependencias.auth import require_client_header
from app.nucleo.dependencias.autorizacion import Owner
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter

router = APIRouter(prefix="/documents/external/wikipedia", tags=["external sources"])
LIMITER = AuthRateLimiter(limit=20)


def limited_owner(user: Owner):
    if not LIMITER.allow(str(user.id)):
        raise HTTPException(429, "Espera un minuto antes de consultar más fuentes.",
                            headers={"Retry-After": "60"})
    return user


def get_wikipedia():
    return MediaWikiService()


Wiki = Annotated[MediaWikiService, Depends(get_wikipedia)]
Reader = Annotated[object, Depends(limited_owner)]


@router.get("/search", response_model=list[WikiResult])
def search(user: Reader, wiki: Wiki, q: Annotated[str, Query(min_length=2, max_length=160)]):
    q = q.strip()
    if len(q) < 2 or any(ord(c) < 32 for c in q):
        raise HTTPException(422, "Escribe un tema de al menos dos caracteres.")
    return wiki.search(q)


@router.get("/preview/{page_id}", response_model=WikiPreview)
def preview(page_id: int, user: Reader, wiki: Wiki):
    if page_id <= 0:
        raise HTTPException(422, "Artículo no válido.")
    result, _ = wiki.preview(page_id)
    return result


@router.post("/import", response_model=DocumentResponse, status_code=201,
             dependencies=[Depends(require_client_header)])
def import_article(request: WikiImport, user: Reader, wiki: Wiki, service: Service):
    # Re-fetch a pinned revision; never trust text, URLs or attribution from the browser.
    result, snapshot = wiki.preview(request.page_id, request.revision_id)
    source = result.source
    if source.text_sha256 != request.text_sha256:
        raise HTTPException(409, "El texto cambió desde la revisión. Vuelve a abrir el artículo.")
    metadata = DocumentMetadata(
        course=request.course, source_reference=source.url,
        permission_note=(f"{source.license_name}; {source.license_url}. "
                         "Reutilización confirmada por el docente; texto adaptado.")[:500],
    )
    payload = (f"{source.title}\n\n{source.attribution}\nOrigen: {source.url}\n"
               f"Licencia: {source.license_name} {source.license_url}\n"
               f"Consultado: {source.retrieved_at.isoformat()}\n"
               "Adaptación: extracción de texto; imágenes y multimedia omitidas.\n\n"
               f"{result.text}\n").encode("utf-8")
    file = UploadFile(file=io.BytesIO(payload),
                      filename=f"wikipedia-{source.page_id}-{source.revision_id}.txt",
                      headers=Headers({"content-type": "text/plain"}))
    try:
        return service.upload(file, source.title[:160], user.id, metadata,
                              external_source=source.model_dump(mode="json"),
                              source_snapshot=snapshot)
    finally:
        file.file.close()


@router.get("/snapshot/{identifier}")
def snapshot(identifier: UUID, user: Owner, service: Service):
    document = service.get(identifier, user.id)
    if not document.external_source:
        raise HTTPException(404, "Este documento no tiene una captura externa.")
    path = service.settings.document_storage_path.resolve() / f"{identifier}.source.json"
    try:
        payload = path.read_bytes()
    except OSError:
        raise HTTPException(409, "La captura original no está disponible.") from None
    if hashlib.sha256(payload).hexdigest() != document.external_source["snapshot_sha256"]:
        raise HTTPException(409, "La integridad de la captura original cambió.")
    return FileResponse(path, media_type="application/json", filename=f"{identifier}-fuente.json",
                        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"})
