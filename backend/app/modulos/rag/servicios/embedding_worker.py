import json
import logging
import sys
from pathlib import Path

from app.modulos.rag.servicios.embedding_service import EmbeddingError, EmbeddingService


def main():
    logging.disable(logging.CRITICAL)
    try:
        if sys.platform != "win32":
            import resource

            resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
            resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
        request = json.loads(sys.stdin.buffer.read(6 * 1024 * 1024))
        service = EmbeddingService(Path(request["model_path"]))
        vectors, counts = service.encode(request["texts"], request.get("kind", "passage"))
        result = {"vectors": vectors, "token_counts": counts}
    except EmbeddingError as error:
        result = {"error": error.code}
    except Exception:
        result = {"error": "embedding_failed"}
    sys.stdout.write(json.dumps(result, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
