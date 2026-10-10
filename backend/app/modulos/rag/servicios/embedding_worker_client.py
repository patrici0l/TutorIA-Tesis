import json
import os
import subprocess
import sys
from pathlib import Path
from threading import BoundedSemaphore

from app.configuracion.settings import Settings

EMBEDDING_SLOTS = BoundedSemaphore(1)


class EmbeddingWorkerClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def encode(self, texts: list[str], kind: str = "passage"):
        if not EMBEDDING_SLOTS.acquire(blocking=False):
            return {"error": "embedding_busy"}
        try:
            return self._run(texts, kind)
        finally:
            EMBEDDING_SLOTS.release()

    def _run(self, texts: list[str], kind: str = "passage"):
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
        try:
            result = json.loads(process.stdout)
            return result if isinstance(result, dict) else {"error": "embedding_failed"}
        except (ValueError, TypeError):
            return {"error": "embedding_failed"}
