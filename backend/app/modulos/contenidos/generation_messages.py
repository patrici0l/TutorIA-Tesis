"""Safe, actionable explanations shared by generation and its saved history."""


def generation_failure_message(code: str | None) -> str:
    messages = {
        "llm_incomplete": (
            "El proveedor devolvió una respuesta incompleta. Prepara un recurso más breve "
            "o un quiz con menos preguntas. No se guardó un recurso utilizable."
        ),
        "llm_timeout": (
            "El proveedor superó el tiempo de espera. No se guardó un recurso utilizable; "
            "puedes preparar otro más adelante."
        ),
        "llm_rate_limit": "El proveedor alcanzó su límite de solicitudes. Inténtalo más adelante.",
        "generation_interrupted": "La generación se interrumpió. No se reintentó automáticamente.",
    }
    return messages.get(code, "La generación terminó sin un recurso válido. No se reintentó.")
