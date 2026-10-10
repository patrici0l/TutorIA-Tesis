import json
import subprocess
import sys
from pathlib import Path
from threading import BoundedSemaphore
from uuid import UUID

from fastapi import HTTPException

from app.configuracion.settings import Settings
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.rag.repositorios.chunk_repository import ChunkRepository

ERROR_MESSAGES = {
    "empty_text": "No se encontró texto extraíble. Un documento escaneado necesita OCR.",
    "unsupported_document": (
        "Este contenido requiere una conversión previa; "
        "OfficeMath y algunos estilos matemáticos heredados aún no están admitidos."
    ),
    "invalid_document": "No se pudo leer la estructura del documento.",
    "extraction_limit": (
        "El documento supera los límites de texto, páginas o fragmentos de esta etapa."
    ),
    "file_missing": "El archivo privado no está disponible. Vuelve a cargar el documento.",
    "file_unavailable": "No se pudo acceder al archivo privado de forma segura.",
    "file_changed": "El archivo no coincide con la copia cargada. Vuelve a cargar el documento.",
    "extraction_timeout": (
        "La extracción superó el tiempo permitido. Prueba con un documento más pequeño."
    ),
    "extraction_failed": "No se pudo procesar el documento. Puedes volver a intentarlo.",
}

# Bounded per API process. Additional API replicas require a shared job queue.
EXTRACTION_SLOTS = BoundedSemaphore(2)


class IngestDocumentService:
    def __init__(self, documents: DocumentService, repository: ChunkRepository, settings: Settings):
        self.documents, self.repository, self.settings = documents, repository, settings

    def process(self, identifier: UUID, owner: UUID):
        document = self.documents.get(identifier, owner)
        if document.processing_status == "processed":
            return document
        # Capture immutable file metadata before claiming. claim commits the read
        # transaction; extraction must not hold a database transaction open.
        request = {
            "path": str(self.settings.document_storage_path.resolve() / str(identifier)),
            "size_bytes": document.size_bytes,
            "sha256": document.sha256,
            "mime_type": document.mime_type,
            "max_bytes": self.settings.document_max_bytes,
            "chunk_chars": self.settings.document_chunk_chars,
            "chunk_overlap": self.settings.document_chunk_overlap,
        }
        if not EXTRACTION_SLOTS.acquire(blocking=False):
            raise HTTPException(
                429, "Hay dos documentos en procesamiento. Inténtalo en un momento."
            )
        try:
            token = self.repository.claim(identifier, owner)
            if not token:
                document = self.documents.get(identifier, owner)
                if document.processing_status == "processed":
                    return document
                raise HTTPException(
                    409, "El documento ya se está procesando. Actualiza su detalle."
                )
            try:
                result = self.extract(request)
                if "error" in result:
                    code = result["error"]
                    if code not in ERROR_MESSAGES:
                        code = "extraction_failed"
                    self.repository.fail(identifier, token, code)
                    raise HTTPException(422, ERROR_MESSAGES[code])
                if not self.repository.publish(
                    identifier, token, result["chunks"], result["metadata"]
                ):
                    self.documents.get(identifier, owner)
                    raise HTTPException(409, "El procesamiento cambió. Actualiza el detalle.")
            except HTTPException:
                raise
            except Exception:
                self.repository.db.rollback()
                self.repository.fail(identifier, token, "extraction_failed")
                raise HTTPException(500, ERROR_MESSAGES["extraction_failed"]) from None
            return self.documents.get(identifier, owner)
        finally:
            EXTRACTION_SLOTS.release()

    def extract(self, request: dict) -> dict:
        try:
            process = subprocess.run(
                [sys.executable, "-m", "app.modulos.rag.servicios.extraction_worker"],
                input=json.dumps(request).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).resolve().parents[4],
                timeout=self.settings.extraction_timeout_seconds,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
        except subprocess.TimeoutExpired:
            return {"error": "extraction_timeout"}
        if process.returncode or not process.stdout or len(process.stdout) > 6 * 1024 * 1024:
            return {"error": "extraction_failed"}
        return json.loads(process.stdout)
