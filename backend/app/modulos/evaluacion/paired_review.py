"""Registra respuestas aportadas offline de pares A; no ejecuta ni certifica IA."""

import argparse
import json
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.direct_resource_validation_service import (
    DirectResourceValidationService,
)
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.evaluacion.paired_preparation import digest, read_payload, validate_pair
from app.modulos.proveedores_ia.errors import ErrorCode
from app.modulos.proveedores_ia.schemas import GenerationTarget, TokenUsage


class Attempt(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    attempt_id: UUID
    mode: Literal["direct", "rag"]
    prompt_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    outcome: Literal["response", "provider_failure"]
    text: str | None = Field(default=None, max_length=65536, repr=False)
    error_code: ErrorCode | None = None
    target: GenerationTarget | None = None
    usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: int | None = Field(default=None, ge=0, strict=True)

    @model_validator(mode="after")
    def consistent_outcome(self):
        if self.outcome == "response":
            if self.text is None or self.error_code is not None:
                raise ValueError("Respuesta requiere texto y no código de proveedor.")
        elif self.text is not None or self.error_code is None:
            raise ValueError("Fallo requiere código seguro y no texto parcial.")
        return self


class AttemptBatch(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    evidence_origin: Literal["synthetic_fixture", "declared_provider_output"]
    attempts: list[Attempt] = Field(min_length=1, max_length=100)


def review_blocks(value, path="resource"):
    """Incluye bloques de texto de ambos contratos; no atribuye respaldo por ausencia de citas."""
    if isinstance(value, dict):
        if "text" in value and "citations" in value:
            return [{"path": path, **value, "semantic_verdict": None}]
        return [
            block for key, item in value.items() for block in review_blocks(item, f"{path}.{key}")
        ]
    if isinstance(value, list):
        return [
            block for i, item in enumerate(value) for block in review_blocks(item, f"{path}[{i}]")
        ]
    return []


def build_paired_review(manifest: dict, payload: dict) -> dict:
    validate_pair(manifest)
    batch = AttemptBatch.model_validate(payload)
    if batch.manifest_sha256 != manifest["manifest_sha256"]:
        raise ValueError("Manifiesto ajeno.")
    identifiers = [item.attempt_id for item in batch.attempts]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Intentos repetidos.")
    request = ContentRequest.model_validate(manifest["input"]["request"])
    arms = {arm["mode"]: arm for arm in manifest["arms"]}
    aliases = {source["citation_id"] for source in manifest["reference_sources"]}
    expected_target = manifest["shared_controls"]["target"]
    cases = []
    for attempt in batch.attempts:
        if attempt.prompt_sha256 != arms[attempt.mode]["prompt_sha256"]:
            raise ValueError("Prompt ajeno al brazo.")
        target = attempt.target.model_dump() if attempt.target else None
        if target != expected_target:
            raise ValueError("Modelo/proveedor no coincide con el manifiesto.")
        if batch.evidence_origin == "declared_provider_output" and target is None:
            raise ValueError("Salida de proveedor requiere objetivo declarado.")
        resource, code = None, attempt.error_code
        status = "provider_failure"
        if attempt.outcome == "response":
            try:
                if attempt.mode == "direct":
                    parsed = DirectResourceValidationService().validate(attempt.text, request)
                else:
                    parsed = ResourceValidationService().validate(attempt.text, request, aliases)
                resource = parsed.model_dump(mode="json")
                status = "valid_resource"
            except ContentError as error:
                code = error.code
                status = (
                    "abstained"
                    if code in {"content_unable_to_answer", "content_insufficient_sources"}
                    else "invalid_output"
                )
        cases.append(
            {
                "attempt_id": str(attempt.attempt_id),
                "mode": attempt.mode,
                "prompt_sha256": attempt.prompt_sha256,
                "status": status,
                "error_code": code,
                "response_sha256": digest(attempt.text) if attempt.text is not None else None,
                "target": target,
                "usage": attempt.usage.model_dump(),
                "latency_ms": attempt.latency_ms,
                "resource": resource,
                "review_blocks": review_blocks(resource),
                "semantic_review_status": "pending_human",
            }
        )
    summaries = {}
    for mode in arms:
        rows = [row for row in cases if row["mode"] == mode]
        known = [
            row["usage"]["total_tokens"] for row in rows if row["usage"]["total_tokens"] is not None
        ]
        summaries[mode] = {
            "attempt_count": len(rows),
            **{
                status: sum(row["status"] == status for row in rows)
                for status in ("valid_resource", "provider_failure", "abstained", "invalid_output")
            },
            "known_total_tokens_cases": len(known),
            "known_total_tokens_subtotal": sum(known) if known else None,
            "total_tokens": sum(known) if rows and len(known) == len(rows) else None,
        }
    report = {
        "report_version": "experiment-a-review-v1",
        "manifest_sha256": batch.manifest_sha256,
        "batch_sha256": digest(batch.model_dump(mode="json")),
        "evidence_origin": batch.evidence_origin,
        "reference_sources": manifest["reference_sources"],
        "cases": cases,
        "summary_by_mode": summaries,
        "benchmark_complete": False,
        "limitations": [
            "Registro declarado: no autentica envío, uso medido ni exhaustividad de intentos.",
            "Validación estructural no acredita matemáticas ni respaldo semántico.",
            "Citas vacías directas no son fallo; revisión humana usa las mismas fuentes.",
            "Orden de archivo no acredita orden de ejecución; casos ausentes no son éxitos.",
        ],
    }
    return {**report, "report_sha256": digest(report)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("attempts", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        report = build_paired_review(read_payload(args.manifest), read_payload(args.attempts))
        rendered = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        rendered.encode("utf-8")
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(rendered)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, ContentError):
        parser.exit(1, "Registro inválido o destino no disponible; no se guardó el reporte.\n")
    print("Registro offline guardado; evaluación humana pendiente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
