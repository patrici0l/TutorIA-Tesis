"""Prueba manual de una sola petición; importar este módulo no consume la API."""

import argparse
import json

from app.configuracion.settings import get_settings
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationRequest
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider


def main() -> int:
    parser = argparse.ArgumentParser(description="Una petición Gemini sintética, sin reintentos.")
    parser.add_argument("--free-tier-confirmed", action="store_true", required=True)
    parser.add_argument(
        "--model",
        choices=["gemini-2.5-flash-lite", "gemini-3.1-flash-lite"],
        default="gemini-3.1-flash-lite",
    )
    args = parser.parse_args()
    settings = get_settings().model_copy(
        update={
            "llm_enabled": True,
            "llm_default_provider": "gemini",
            "llm_model": args.model,
            "llm_timeout_seconds": 15,
            "llm_max_input_chars": 1000,
            "llm_max_output_tokens": 128,
            "llm_requests_per_minute": 1,
        }
    )
    try:
        result = create_provider(settings).generate(
            GenerationRequest(
                instructions="Responde brevemente en español. Esta es una prueba sintética.",
                prompt="¿Cuál es la derivada de f(x)=x²? Responde en una sola frase.",
            )
        )
    except ProviderError as error:
        print(json.dumps({"status": "failed", "error_code": error.code, "attempts": 1}))
        return 1
    print(
        json.dumps(
            {
                "status": "succeeded",
                "attempts": 1,
                "provider": result.provider,
                "model": result.requested_model,
                "model_version": result.model_version,
                "latency_ms": result.latency_ms,
                "usage": result.usage.model_dump(),
                "finish_reason": result.finish_reason,
                "output_chars": len(result.text),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
