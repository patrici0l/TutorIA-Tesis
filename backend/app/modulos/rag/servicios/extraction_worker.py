"""Isolated, bounded text extraction. stdout is a private JSON result, never a log."""

import hashlib
import hmac
import json
import logging
import os
import stat
import sys
from dataclasses import asdict
from pathlib import Path

from app.modulos.rag.servicios.document_text_service import (
    EXTRACTOR_VERSION,
    DocumentTextService,
    ExtractionError,
)


def restrict_resources():
    if sys.platform != "win32":
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (384 * 1024 * 1024, 384 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CPU, (20, 20))


def read_private_file(path: Path, expected_size: int, expected_sha256: str, max_bytes: int):
    if path.is_symlink():
        raise ExtractionError("file_unavailable")
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except FileNotFoundError:
        raise ExtractionError("file_missing") from None
    except OSError:
        raise ExtractionError("file_unavailable") from None
    with os.fdopen(descriptor, "rb") as source:
        metadata = os.fstat(source.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > max_bytes:
            raise ExtractionError("file_unavailable")
        payload = source.read(max_bytes + 1)
    if len(payload) != expected_size or not hmac.compare_digest(
        hashlib.sha256(payload).hexdigest(), expected_sha256
    ):
        raise ExtractionError("file_changed")
    return payload


def execute(request: dict):
    payload = read_private_file(
        Path(request["path"]), request["size_bytes"], request["sha256"], request["max_bytes"]
    )
    service = DocumentTextService()
    units = service.extract(payload, request["mime_type"])
    chunks = service.chunk(units, request["chunk_chars"], request["chunk_overlap"])
    hashes = {
        (unit.source_kind, unit.source_index): hashlib.sha256(unit.text.encode("utf-8")).hexdigest()
        for unit in units
    }
    return {
        "chunks": [
            {**asdict(chunk), "source_sha256": hashes[(chunk.source_kind, chunk.source_index)]}
            for chunk in chunks
        ],
        "metadata": {
            "text_chars": sum(len(unit.text) for unit in units),
            "chunk_count": len(chunks),
            "processing_version": EXTRACTOR_VERSION,
            "chunk_chars": request["chunk_chars"],
            "chunk_overlap": request["chunk_overlap"],
        },
    }


def main():
    logging.disable(logging.CRITICAL)
    try:
        restrict_resources()
        request = json.loads(sys.stdin.buffer.read(4096))
        result = execute(request)
    except ExtractionError as error:
        result = {"error": error.code}
    except Exception:
        result = {"error": "extraction_failed"}
    sys.stdout.write(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
