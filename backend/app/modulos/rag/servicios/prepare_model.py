"""Explicit download of pinned public model files; never called from an API request."""

import hashlib
import urllib.request
from pathlib import Path
from uuid import uuid4

from app.configuracion.settings import get_settings
from app.modulos.rag.servicios.model_spec import ARTIFACTS, MODEL_ID, MODEL_REVISION


def verified(path: Path, size: int, digest: str) -> bool:
    if path.is_symlink() or not path.is_file() or path.stat().st_size != size:
        return False
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest() == digest


def prepare(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    for filename, (size, digest) in ARTIFACTS.items():
        target = directory / filename
        if verified(target, size, digest):
            print(f"Verified: {filename}", flush=True)
            continue
        temporary = directory / f"{filename}.download-{uuid4().hex}"
        url = f"https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/onnx/{filename}"
        try:
            print(f"Downloading public artifact: {filename} ({size} bytes)", flush=True)
            with (
                urllib.request.urlopen(url, timeout=60) as response,
                temporary.open("xb") as output,
            ):
                total = 0
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > size:
                        raise ValueError("Artifact size mismatch")
                    output.write(block)
            if not verified(temporary, size, digest):
                raise ValueError("Artifact checksum mismatch")
            temporary.replace(target)
            print(f"Verified: {filename}", flush=True)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        prepare(get_settings().embedding_model_path)
    except Exception:
        raise SystemExit("Model preparation failed; private diagnostics omitted") from None
