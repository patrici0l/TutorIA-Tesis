"""Descubre publicaciones en CORE; nunca descarga URLs recibidas de terceros."""

import hashlib
import json
from datetime import UTC, datetime

import httpx
from fastapi import HTTPException

from app.modulos.documentos.core_schemas import CorePreview, CoreResult

BASE = "https://api.core.ac.uk/v3"
MAX_BYTES = 2_000_000


class CoreService:
    def __init__(self, transport=None):
        self.transport = transport

    def request(self, path, params=None):
        try:
            with httpx.Client(
                transport=self.transport, timeout=20, follow_redirects=False
            ) as client:
                with client.stream(
                    "GET",
                    BASE + path,
                    params=params,
                    headers={
                        "User-Agent": "TutorIA/0.3 (educational research; CORE discovery)",
                        "Accept": "application/json",
                    },
                ) as response:
                    if response.status_code == 429:
                        raise HTTPException(
                            429,
                            "CORE alcanzó su límite. Espera y vuelve a intentar.",
                            headers={"Retry-After": "60"},
                        )
                    if response.status_code == 404:
                        raise HTTPException(404, "La publicación ya no está disponible en CORE.")
                    if response.status_code in {401, 403}:
                        raise HTTPException(
                            503, "CORE restringió el acceso público. No se importó ningún material."
                        )
                    if response.status_code != 200:
                        raise HTTPException(503, "CORE no está disponible en este momento.")
                    payload = bytearray()
                    for chunk in response.iter_bytes():
                        payload.extend(chunk)
                        if len(payload) > MAX_BYTES:
                            raise HTTPException(
                                502, "La respuesta de CORE supera el tamaño permitido."
                            )
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (httpx.HTTPError, ValueError, UnicodeError):
            raise HTTPException(503, "No se pudo consultar CORE. Inténtalo de nuevo.") from None

    @staticmethod
    def result(row):
        identifier = row.get("id")
        if isinstance(identifier, str) and identifier.isdecimal():
            identifier = int(identifier)
        title = row.get("title")
        if type(identifier) is not int or identifier <= 0 or not isinstance(title, str):
            raise HTTPException(502, "CORE devolvió una ficha incompleta.")
        authors = row.get("authors") or []
        if not isinstance(authors, list):
            authors = []
        year = row.get("yearPublished")
        language = row.get("language")
        language = language.get("code") if isinstance(language, dict) else None
        return CoreResult(
            work_id=identifier,
            title=title.strip()[:500],
            authors=[
                a["name"][:200]
                for a in authors[:30]
                if isinstance(a, dict) and isinstance(a.get("name"), str)
            ],
            year=year if type(year) is int and 1000 <= year <= 2200 else None,
            language=language[:20] if isinstance(language, str) else None,
        )

    def search(self, query):
        # La barra final evita una redirección del proveedor.
        data = self.request("/search/works/", {"q": query, "limit": 5})
        rows = data.get("results")
        if not isinstance(rows, list):
            raise HTTPException(502, "CORE no devolvió una lista de resultados válida.")
        return [self.result(row) for row in rows[:5] if isinstance(row, dict)]

    def preview(self, work_id):
        data = self.request(f"/works/{work_id}")
        result = self.result(data)
        if result.work_id != work_id:
            raise HTTPException(502, "La ficha recibida no corresponde a la publicación elegida.")
        snapshot = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        abstract = data.get("abstract")
        full_text = data.get("fullText")
        license_value = data.get("license")
        return CorePreview(
            **result.model_dump(),
            url=f"https://core.ac.uk/works/{work_id}",
            abstract=abstract[:20000] if isinstance(abstract, str) else "",
            record_sha256=hashlib.sha256(snapshot).hexdigest(),
            retrieved_at=datetime.now(UTC),
            license_statement=license_value[:500]
            if isinstance(license_value, str) and license_value.strip()
            else "La ficha no informa una licencia de reutilización.",
            full_text_available=isinstance(full_text, str)
            and len(full_text.strip()) > 200
            and not full_text.lower().startswith("not available"),
        ), snapshot
