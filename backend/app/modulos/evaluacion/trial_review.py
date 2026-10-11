"""Revisa tres resultados terminales sintéticos, incluidos fallos, sin BD ni proveedor."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import get_args

from app.modulos.contenidos.errors import CONTENT_ERRORS, ContentError
from app.modulos.contenidos.history_schemas import HistoryDetail
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.resource_validation_service import (
    ResourceValidationService,
    unique_object,
)
from app.modulos.evaluacion.offline_review import DIMENSIONS, cited_claims
from app.modulos.proveedores_ia.errors import ErrorCode

LEVELS = ("low", "medium", "high")


def build_trial_review(rows: list[dict]) -> dict:
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("Se requieren los tres niveles, incluidos los fallos.")
    cases, requests, profiles, sources, targets, configurations, starts = [], [], [], [], [], [], []
    identifiers, levels = set(), set()
    for row in rows:
        level = row["level"]
        detail = HistoryDetail.model_validate(row["history"])
        preparation, audit = detail.preparation, detail.audit
        if (
            level not in LEVELS
            or level in levels
            or preparation.id in identifiers
            or preparation.adaptation is None
            or preparation.adaptation.profile.mastery_level != level
            or detail.status not in {"succeeded", "failed"}
            or audit is None
            or audit.generation_started_at is None
            or audit.provider is None
            or audit.requested_model is None
            or detail.completed_at is None
        ):
            raise ValueError("Faltan datos terminales o el nivel/identificador es inconsistente.")
        started, completed = audit.generation_started_at, detail.completed_at
        if started.utcoffset() is None or completed.utcoffset() is None or completed < started:
            raise ValueError("Fechas terminales inconsistentes o sin zona horaria.")
        profile = preparation.adaptation.profile
        # ProfileResponse ya exige data_kind synthetic. No anonimiza texto libre.
        request = ContentRequest(
            topic=preparation.topic,
            learning_objective=preparation.learning_objective,
            resource_type=preparation.resource_type,
            difficulty=preparation.difficulty,
            question_count=preparation.question_count,
            # El historial público no expone la respuesta de FEEDBACK. No inventarla.
        )
        identifiers.add(preparation.id)
        levels.add(level)
        source_values = [source.model_dump(mode="json") for source in preparation.sources]
        aliases = [source.citation_id for source in preparation.sources]
        if not aliases or len(set(aliases)) != len(aliases):
            raise ValueError("Fuentes ausentes o aliases duplicados.")
        claims = []
        if detail.status == "succeeded":
            if detail.resource is None or audit.error_code is not None:
                raise ValueError("Éxito sin recurso o con error.")
            validated = ResourceValidationService().validate(
                detail.resource.model_dump_json(), request, set(aliases)
            )
            claims = list(cited_claims(validated))
        elif detail.resource is not None or (
            audit.error_code is not None
            and audit.error_code not in CONTENT_ERRORS | set(get_args(ErrorCode))
        ):
            raise ValueError("Fallo con contenido o sin código seguro.")
        configuration = (
            audit.execution_configuration.model_dump(mode="json")
            if audit.execution_configuration
            else None
        )
        configurations.append(configuration)
        requests.append(request.model_dump(exclude={"difficulty"}))
        profiles.append(
            profile.model_dump(
                mode="json", exclude={"id", "created_at", "student_id", "mastery_level"}
            )
        )
        sources.append(source_values)
        targets.append(
            {
                "provider": audit.provider,
                "requested_model": audit.requested_model,
                "prompt_version": audit.prompt_version,
                "policy_version": preparation.adaptation.policy_version,
            }
        )
        starts.append(started)
        cases.append(
            {
                "id": str(preparation.id),
                "level": level,
                "status": detail.status,
                "difficulty": preparation.difficulty,
                "request": request.model_dump(mode="json", exclude={"student_answer"}),
                "provider": audit.provider,
                "requested_model": audit.requested_model,
                "prompt_version": audit.prompt_version,
                "policy_version": preparation.adaptation.policy_version,
                "adaptation_guidance": preparation.adaptation.guidance,
                "focus_errors": preparation.adaptation.focus_errors,
                "generation_started_at": started.isoformat(),
                "completed_at": completed.isoformat(),
                "prompt_sha256": audit.prompt_sha256,
                "model_version": audit.model_version,
                "error_code": audit.error_code,
                "usage": audit.usage.model_dump() if audit.usage else None,
                "latency_ms": audit.latency_ms,
                "estimated_cost": str(audit.estimated_cost)
                if audit.estimated_cost is not None
                else None,
                "cost_basis": audit.cost_basis.model_dump(mode="json")
                if audit.cost_basis
                else None,
                "execution_configuration": configuration,
                "sources": source_values,
                "claims": claims,
                "review": {name: {"verdict": None, "evidence": None} for name in DIMENSIONS},
                "content_review_available": detail.status == "succeeded",
            }
        )
    controls = {
        "same_request_except_difficulty": all(item == requests[0] for item in requests),
        "same_profile_except_level_and_identity": all(item == profiles[0] for item in profiles),
        "same_sources_snapshot": all(item == sources[0] for item in sources),
        "same_requested_provider_model_prompt_policy": all(item == targets[0] for item in targets),
    }
    known_configuration_count = sum(item is not None for item in configurations)
    limits_match = (
        all(item == configurations[0] for item in configurations)
        if known_configuration_count == 3
        else None
    )
    comparable = all(controls.values()) and limits_match is True
    valid = sum(case["status"] == "succeeded" for case in cases)
    totals = [case["usage"]["total_tokens"] if case["usage"] else None for case in cases]
    known_totals = [value for value in totals if value is not None]
    known_sum = sum(known_totals) if known_totals else None
    return {
        "report_version": "synthetic-terminal-trial-v1",
        "semantic_review_status": "pending_human",
        "case_count": 3,
        "valid_resource_count": valid,
        "failed_case_count": 3 - valid,
        "mechanical_checks": controls,
        "execution_configuration_known_cases": known_configuration_count,
        "same_recorded_execution_configuration": limits_match,
        "recorded_controls_match": comparable,
        "control_evidence_status": (
            "different_controls"
            if not all(controls.values()) or limits_match is False
            else "complete_recorded_controls"
            if comparable
            else "incomplete_evidence"
        ),
        "three_level_content_available": valid == 3,
        "ready_for_controlled_semantic_review": valid == 3 and comparable,
        "known_total_tokens_sum": known_sum,
        "total_tokens_known_cases": len(known_totals),
        "batch_total_tokens": known_sum if len(known_totals) == 3 else None,
        "generation_start_span_seconds": (max(starts) - min(starts)).total_seconds(),
        "limitations": [
            "Los fallos cuentan; no se reconstruye contenido truncado.",
            "Sin límites guardados no se presume configuración igual ni defaults actuales.",
            "Controles coincidentes no prueban causalidad, estabilidad ni mejora del aprendizaje.",
            "Citas y contratos válidos no certifican respaldo semántico; revisión pendiente.",
            "FEEDBACK requiere evidencia privada adicional; no se admite en este formato.",
        ],
        "cases": sorted(cases, key=lambda case: LEVELS.index(case["level"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        type=Path,
        nargs=3,
        metavar="HISTORY",
        help="Historial low, medium, high, en ese orden",
    )
    parser.add_argument("output", type=Path, help="Informe nuevo; nunca sobrescribe archivos")
    args = parser.parse_args()
    try:
        rows, provenance = [], []
        for level, path in zip(LEVELS, args.inputs):
            raw = path.read_bytes()
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("Entrada demasiado grande.")
            rows.append(
                {
                    "level": level,
                    "history": json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object),
                }
            )
            provenance.append({"level": level, "input_sha256": hashlib.sha256(raw).hexdigest()})
        report = build_trial_review(rows)
        report["input_files"] = provenance
        payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        payload.encode("utf-8")  # Rechazar texto inválido antes de abrir el destino.
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(payload)
    except (OSError, ValueError, TypeError, KeyError, ContentError):
        parser.exit(
            1, "No se creó el informe: evidencia inválida o destino existente/no disponible.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
