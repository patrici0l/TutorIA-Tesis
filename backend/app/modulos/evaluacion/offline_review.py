"""Prepara revisión de evidencia sintética guardada, sin BD, configuración ni proveedor."""

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.schemas import CitedText, ContentRequest
from app.modulos.contenidos.servicios.resource_validation_service import (
    ResourceValidationService,
    unique_object,
)
from app.modulos.perfiles.schemas import ProfileResponse
from app.modulos.proveedores_ia.schemas import TokenUsage

REVIEW_VERSION = "synthetic-review-v1"
DIMENSIONS = (
    "fidelity_to_sources",
    "objective_scope",
    "mathematical_correctness",
    "difficulty_and_support",
    "clarity",
)


def cited_claims(value, path="resource"):
    if isinstance(value, CitedText):
        yield {
            "path": path,
            "text": value.text,
            "citations": value.citations,
            "source_support": None,
            "reviewer_note": None,
        }
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            yield from cited_claims(getattr(value, name), f"{path}.{name}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from cited_claims(item, f"{path}[{index}]")


def build_review(rows: list[dict]) -> dict:
    """Comprobaciones mecánicas; ninguna equivalencia implica calidad pedagógica."""
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("Se requieren tres resultados, uno por nivel.")
    cases, fixed_requests, fixed_profiles, source_sets, targets, starts = [], [], [], [], [], []
    identifiers, levels = set(), set()
    for row in rows:
        identifier = str(UUID(row["id"]))
        profile = ProfileResponse.model_validate(row["profile"])
        level = row["level"]
        if (
            row["status"] != "succeeded"
            or level != profile.mastery_level
            or level in levels
            or identifier in identifiers
        ):
            raise ValueError("Resultados repetidos, incompletos o con nivel inconsistente.")
        identifiers.add(identifier)
        levels.add(level)
        request = ContentRequest.model_validate(row["request"])
        sources = row["sources"]
        if not isinstance(sources, list) or not sources:
            raise ValueError("Faltan las fuentes guardadas.")
        citations = [source["citation_id"] for source in sources]
        if len(citations) != len(set(citations)):
            raise ValueError("Referencias de fuente duplicadas.")
        resource = ResourceValidationService().validate(
            json.dumps(row["resource"], ensure_ascii=False), request, set(citations)
        )
        if not re.fullmatch(r"[0-9a-f]{64}", row["prompt_sha256"]):
            raise ValueError("Hash de prompt inválido.")
        started = datetime.fromisoformat(row["generation_started_at"].replace("Z", "+00:00"))
        if started.utcoffset() is None:
            raise ValueError("La fecha de inicio necesita zona horaria.")
        starts.append(started)
        usage = TokenUsage.model_validate(row["usage"]) if row["usage"] is not None else None
        fixed_requests.append(request.model_dump(exclude={"difficulty"}))
        fixed_profiles.append(profile.model_dump(
            exclude={"id", "created_at", "student_id", "mastery_level"}, mode="json"
        ))
        source_sets.append(sources)
        targets.append({name: row[name] for name in (
            "provider", "requested_model", "model_version", "prompt_version", "policy_version"
        )})
        cases.append({
            "id": identifier,
            "level": level,
            "difficulty": request.difficulty,
            "prompt_sha256": row["prompt_sha256"],
            "generation_started_at": started.isoformat(),
            "usage": usage.model_dump() if usage else None,
            "claims": list(cited_claims(resource)),
            "review": {dimension: {"verdict": None, "evidence": None}
                       for dimension in DIMENSIONS},
        })
    checks = {
        "same_request_except_difficulty": all(item == fixed_requests[0] for item in fixed_requests),
        "same_profile_except_level_and_identity": all(
            item == fixed_profiles[0] for item in fixed_profiles
        ),
        "same_sources_snapshot": all(item == source_sets[0] for item in source_sets),
        "same_provider_model_prompt_policy": all(item == targets[0] for item in targets),
    }
    totals = [case["usage"]["total_tokens"] if case["usage"] else None for case in cases]
    return {
        "review_version": REVIEW_VERSION,
        "semantic_review_status": "pending",
        "mechanical_checks": checks,
        "mechanically_comparable": all(checks.values()),
        "generation_start_span_seconds": (max(starts) - min(starts)).total_seconds(),
        "known_total_tokens_sum": sum(value for value in totals if value is not None),
        "total_tokens_known_cases": sum(value is not None for value in totals),
        "case_count": len(cases),
        "limitations": [
            "Citas válidas no certifican respaldo semántico ni corrección matemática.",
            "Una salida por nivel no demuestra mejora del aprendizaje ni controla aleatoriedad.",
            "No se comprueban aquí parámetros de envío ausentes ni facturación.",
            "Las dimensiones requieren revisión humana con evidencia; null significa pendiente.",
        ],
        "cases": sorted(cases, key=lambda case: ("low", "medium", "high").index(case["level"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON de tres resultados sintéticos guardados")
    parser.add_argument("output", type=Path, help="Archivo nuevo; nunca sobrescribe evidencia")
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("Evidencia demasiado grande.")
        rows = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
        report = build_review(rows)
        report["input_sha256"] = hashlib.sha256(raw).hexdigest()
        # Modo exclusivo incluso si input/output apuntan al mismo archivo.
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(report, output, ensure_ascii=False, indent=2, allow_nan=False)
            output.write("\n")
    except (OSError, ValueError, TypeError, KeyError, ContentError):
        parser.exit(
            1, "No se creó la revisión: entrada inválida o salida existente/no disponible.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
