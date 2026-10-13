"""Recorre pares con respuestas HTTP sintéticas; nunca abre transporte de red."""

import argparse
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.configuracion.settings import Settings
from app.modulos.contenidos.errors import ContentError
from app.modulos.evaluacion.paired_assessment import prepare_pair_assessment
from app.modulos.evaluacion.paired_preparation import digest, read_payload, validate_pair
from app.modulos.evaluacion.paired_review import build_paired_review
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationRequest
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider
from app.modulos.proveedores_ia.servicios.request_limiter import RequestLimiter


class SimulationSettings(Settings):
    @classmethod
    def settings_customise_sources(cls, settings_cls, **sources):
        # No leer .env, variables de entorno ni archivos de secretos del operador.
        return (sources["init_settings"],)


class SyntheticResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    status_code: int = Field(ge=200, le=599, strict=True)
    body: dict


class SyntheticResponses(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    direct: SyntheticResponse
    rag: SyntheticResponse


def simulate_pair(manifest: dict, responses: dict) -> dict:
    validate_pair(manifest)
    fixtures = SyntheticResponses.model_validate(responses)
    json.dumps(responses, allow_nan=False)
    controls = manifest["shared_controls"]
    target = controls["target"]
    if target is None or target["provider"] not in {"openai", "claude"}:
        raise ValueError("La simulación requiere un objetivo OpenAI o Claude explícito.")
    if controls["max_output_tokens"] is None or controls["timeout_seconds"] is None:
        raise ValueError("El manifiesto debe fijar límites de salida y timeout.")
    settings = SimulationSettings(
        llm_enabled=True,
        llm_default_provider=target["provider"],
        llm_model=target["requested_model"],
        openai_api_key="synthetic-offline-key",
        anthropic_api_key="synthetic-offline-key",
        llm_max_input_chars=controls["max_input_chars"],
        llm_max_output_tokens=controls["max_output_tokens"],
        llm_timeout_seconds=controls["timeout_seconds"],
    )
    attempts = []
    for arm in manifest["arms"]:
        fixture = getattr(fixtures, arm["mode"])

        def respond(request):
            return httpx.Response(fixture.status_code, json=fixture.body)

        provider = create_provider(
            settings, transport=httpx.MockTransport(respond), limiter=RequestLimiter()
        )
        attempt = {
            "attempt_id": str(uuid5(NAMESPACE_URL, digest([manifest, responses, arm["mode"]]))),
            "mode": arm["mode"],
            "prompt_sha256": arm["prompt_sha256"],
            "target": target,
            # El tiempo del proceso local no representa latencia del proveedor.
            "latency_ms": None,
        }
        try:
            result = provider.generate(GenerationRequest.model_validate(arm["generation_request"]))
            attempt.update(outcome="response", text=result.text, usage=result.usage.model_dump())
        except ProviderError as error:
            attempt.update(
                outcome="provider_failure",
                error_code=error.code,
                usage=error.metadata.usage.model_dump() if error.metadata else {},
            )
        attempts.append(attempt)
    batch = {
        "manifest_sha256": manifest["manifest_sha256"],
        "evidence_origin": "synthetic_fixture",
        "attempts": attempts,
    }
    return {
        "version": "pair-simulation-v1",
        "evidence_origin": "synthetic_fixture",
        "responses_sha256": digest(responses),
        "manifest": manifest,
        "batch": batch,
        "report": build_paired_review(manifest, batch),
        "assessment_template": prepare_pair_assessment(manifest, batch),
        "benchmark_complete": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("responses", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        bundle = simulate_pair(read_payload(args.manifest), read_payload(args.responses))
        rendered = json.dumps(bundle, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        rendered.encode("utf-8")
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(rendered)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, ContentError):
        parser.exit(1, "Simulación inválida o destino no disponible.\n")
    print("Simulación local guardada; no representa resultados reales ni revisión humana.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
