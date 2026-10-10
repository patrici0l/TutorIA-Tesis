class ContentError(Exception):
    """Código seguro, sin respuestas estudiantiles, documentos o salida LLM."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
