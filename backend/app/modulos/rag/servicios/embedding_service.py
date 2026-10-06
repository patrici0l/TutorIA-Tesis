from pathlib import Path

import numpy as np
from tokenizers import Tokenizer

from app.modulos.rag.servicios.model_spec import ARTIFACTS, DIMENSIONS, MAX_TOKENS
from app.modulos.rag.servicios.prepare_model import verified


class EmbeddingError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def normalize_pool(hidden: np.ndarray, mask: np.ndarray):
    pooled = (hidden * mask[..., None]).sum(axis=1) / mask.sum(axis=1)[:, None]
    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    if not np.isfinite(pooled).all() or (norms <= 0).any():
        raise EmbeddingError("invalid_embedding")
    return (pooled / norms).astype(np.float32)


class EmbeddingService:
    def __init__(self, directory: Path):
        for filename, (size, digest) in ARTIFACTS.items():
            if not verified(directory / filename, size, digest):
                raise EmbeddingError("model_unavailable")
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
        import onnxruntime as ort

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.log_severity_level = 4
        self.session = ort.InferenceSession(
            str(directory / "model.onnx"), sess_options=options, providers=["CPUExecutionProvider"]
        )

    def encode(self, texts: list[str], kind: str = "passage"):
        if kind not in {"passage", "query"} or not texts or len(texts) > 1000:
            raise EmbeddingError("invalid_input")
        encoded = []
        for text in texts:
            if not isinstance(text, str) or not text.strip() or len(text) > 2000:
                raise EmbeddingError("invalid_input")
            item = self.tokenizer.encode(f"{kind}: {text}")
            if len(item.ids) > MAX_TOKENS:
                raise EmbeddingError("token_limit")
            encoded.append(item)
        vectors, counts = [], []
        inputs = {item.name for item in self.session.get_inputs()}
        for item in encoded:
            ids = np.array([item.ids], dtype=np.int64)
            mask = np.array([item.attention_mask], dtype=np.int64)
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in inputs:
                feed["token_type_ids"] = np.array([item.type_ids], dtype=np.int64)
            hidden = self.session.run(None, feed)[0]
            vector = normalize_pool(hidden, mask)[0]
            if vector.shape != (DIMENSIONS,):
                raise EmbeddingError("invalid_embedding")
            vectors.append(vector.tolist())
            counts.append(len(item.ids))
        return vectors, counts
