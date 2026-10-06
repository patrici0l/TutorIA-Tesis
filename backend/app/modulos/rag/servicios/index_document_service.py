import json
import math
import os
import subprocess
import sys
from pathlib import Path
from threading import BoundedSemaphore
from uuid import UUID

from fastapi import HTTPException

from app.configuracion.settings import Settings
from app.modulos.documentos.servicios.document_service import DocumentService
from app.modulos.rag.repositorios.index_repository import IndexRepository
from app.modulos.rag.servicios.model_spec import DIMENSIONS, EMBEDDING_VERSION, MODEL_REVISION

INDEX_SLOTS = BoundedSemaphore(1)
INDEX_ERRORS = {
    "model_unavailable": (
        "El modelo local no está preparado o no supera la verificación de integridad."
    ),
    "token_limit": (
        "Un fragmento supera 512 tokens. Carga el material con una segmentación más pequeña."
    ),
    "embedding_timeout": "La indexación superó el tiempo permitido. Prueba con menos material.",
    "embedding_failed": "No se pudo generar el índice. Puedes reintentarlo.",
    "invalid_embedding": "El modelo no produjo vectores válidos. El índice no se publicó.",
}


def validated_vectors(result: dict, snapshot: list[tuple]):
    vectors, counts = result["vectors"], result["token_counts"]
    if len(vectors) != len(snapshot) or len(counts) != len(snapshot) or not snapshot:
        raise ValueError("Incomplete embeddings")
    rows = []
    for (identifier, _), vector, count in zip(snapshot, vectors, counts, strict=True):
        if (
            not isinstance(vector, list)
            or len(vector) != DIMENSIONS
            or any(type(value) not in {int, float} or not math.isfinite(value) for value in vector)
            or abs(sum(value * value for value in vector) - 1) > 0.001
            or type(count) is not int
            or not 1 <= count <= 512
        ):
            raise ValueError("Invalid embeddings")
        rows.append({"id": identifier, "embedding": vector, "embedding_tokens": count})
    return rows


class IndexDocumentService:
    def __init__(self, documents: DocumentService, repository: IndexRepository, settings: Settings):
        self.documents, self.repository, self.settings = documents, repository, settings

    def index(self, identifier: UUID, owner: UUID, rebuild: bool = False):
        document = self.documents.get(identifier, owner)
        if document.processing_status != "processed":
            raise HTTPException(409, "Primero procesa el texto del documento.")
        if document.index_status == "indexed" and not rebuild:
            if (
                document.embedding_revision != MODEL_REVISION
                or document.embedding_version != EMBEDDING_VERSION
            ):
                raise HTTPException(
                    409, "El índice usa otra versión. Se requiere una reconstrucción explícita."
                )
            return document
        if not INDEX_SLOTS.acquire(blocking=False):
            raise HTTPException(429, "Ya hay una indexación en curso. Inténtalo en un momento.")
        try:
            token = self.repository.claim(identifier, owner, rebuild)
            if not token:
                document = self.documents.get(identifier, owner)
                if document.index_status == "indexed":
                    return self.index(identifier, owner)
                raise HTTPException(409, "La indexación sigue en curso. Actualiza el detalle.")
            try:
                snapshot = self.repository.snapshot(identifier)
                result = self.embed([text for _, text in snapshot])
                if "error" in result:
                    code = (
                        result["error"] if result["error"] in INDEX_ERRORS else "embedding_failed"
                    )
                    self.repository.fail(identifier, token, code)
                    raise HTTPException(
                        503 if code == "model_unavailable" else 422, INDEX_ERRORS[code]
                    )
                try:
                    rows = validated_vectors(result, snapshot)
                except (ValueError, KeyError, TypeError):
                    self.repository.fail(identifier, token, "invalid_embedding")
                    raise HTTPException(422, INDEX_ERRORS["invalid_embedding"]) from None
                if not self.repository.publish(identifier, token, rows):
                    self.documents.get(identifier, owner)
                    raise HTTPException(409, "El documento cambió. Actualiza su detalle.")
            except HTTPException:
                raise
            except Exception:
                self.repository.db.rollback()
                self.repository.fail(identifier, token, "embedding_failed")
                raise HTTPException(500, INDEX_ERRORS["embedding_failed"]) from None
            return self.documents.get(identifier, owner)
        finally:
            INDEX_SLOTS.release()

    def embed(self, texts: list[str], kind: str = "passage"):
        environment = {
            **os.environ,
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "TOKENIZERS_PARALLELISM": "false",
        }
        try:
            process = subprocess.run(
                [sys.executable, "-m", "app.modulos.rag.servicios.embedding_worker"],
                input=json.dumps(
                    {
                        "texts": texts,
                        "kind": kind,
                        "model_path": str(self.settings.embedding_model_path.resolve()),
                    }
                ).encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).resolve().parents[4],
                env=environment,
                timeout=self.settings.embedding_timeout_seconds,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
        except subprocess.TimeoutExpired:
            return {"error": "embedding_timeout"}
        if process.returncode or not process.stdout or len(process.stdout) > 12 * 1024 * 1024:
            return {"error": "embedding_failed"}
        return json.loads(process.stdout)
