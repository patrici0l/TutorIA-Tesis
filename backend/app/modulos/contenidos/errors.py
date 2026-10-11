CONTENT_ERRORS = {
    "content_target_mismatch",
    "content_wrong_resource",
    "content_quiz_count",
    "content_invalid_citations",
    "content_invalid_output",
    "content_insufficient_sources",
    "generation_interrupted",
}


class ContentError(Exception):
    """Código seguro, sin respuestas estudiantiles, documentos o salida LLM."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
