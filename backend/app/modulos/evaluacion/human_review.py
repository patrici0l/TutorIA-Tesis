"""Prepare or validate declared human assessments of saved histories; no provider or DB."""

import argparse
import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.servicios.resource_validation_service import unique_object
from app.modulos.evaluacion.offline_review import DIMENSIONS
from app.modulos.evaluacion.trial_review import LEVELS, build_trial_review


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict: Literal["meets", "partially_meets", "does_not_meet"] | None = None
    evidence: str | None = Field(default=None, min_length=1, max_length=4000)

    @model_validator(mode="after")
    def paired(self):
        if (self.verdict is None) != (self.evidence is None) or (
            self.evidence is not None and not self.evidence.strip()
        ):
            raise ValueError("Una decisión requiere evidencia concreta; pendiente usa dos null.")
        return self


class ClaimDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    support: Literal["supported", "partial", "unsupported"] | None = None
    evidence: str | None = Field(default=None, min_length=1, max_length=4000)
    source_aliases: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def paired(self):
        if (self.support is None) != (self.evidence is None) or (
            self.evidence is not None and not self.evidence.strip()
        ):
            raise ValueError("Un juicio de respaldo requiere evidencia.")
        if self.support is None and self.source_aliases:
            raise ValueError("Una afirmación pendiente no tiene referencias de revisión.")
        if self.support in {"supported", "partial"} and not self.source_aliases:
            raise ValueError("El respaldo declarado requiere una referencia citada.")
        if len(self.source_aliases) != len(set(self.source_aliases)):
            raise ValueError("Referencias de revisión duplicadas.")
        return self


class CaseAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    level: Literal["low", "medium", "high"]
    status: Literal["succeeded", "failed"]
    content_review_available: bool = Field(strict=True)
    context: dict
    dimensions: dict[str, Decision]
    claims: list[ClaimDecision]


class Assessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["declared-human-review-v1"]
    input_files: list[dict[str, str]]
    reviewer_name: str | None = Field(default=None, min_length=1, max_length=160)
    reviewed_at: datetime | None = None
    cases: list[CaseAssessment]

    @model_validator(mode="after")
    def identity(self):
        if (self.reviewer_name is None) != (self.reviewed_at is None):
            raise ValueError("Nombre y fecha del revisor se declaran juntos.")
        if self.reviewer_name is not None and not self.reviewer_name.strip():
            raise ValueError("Nombre vacío.")
        if self.reviewed_at is not None and (
            self.reviewed_at.utcoffset() is None or self.reviewed_at > datetime.now(UTC)
        ):
            raise ValueError("Fecha sin zona horaria o futura.")
        return self


def prepare_assessment(report, provenance):
    cases = []
    for case in report["cases"]:
        cases.append(
            {
                "id": case["id"],
                "level": case["level"],
                "status": case["status"],
                "content_review_available": case["content_review_available"],
                "context": {
                    key: copy.deepcopy(case[key])
                    for key in ("request", "adaptation_guidance", "sources", "claims", "error_code")
                },
                "dimensions": {name: {"verdict": None, "evidence": None} for name in DIMENSIONS},
                "claims": [
                    {"path": claim["path"], "support": None, "evidence": None, "source_aliases": []}
                    for claim in case["claims"]
                ],
            }
        )
    return {
        "version": "declared-human-review-v1",
        "input_files": copy.deepcopy(provenance),
        "reviewer_name": None,
        "reviewed_at": None,
        "cases": cases,
    }


def apply_assessment(report, provenance, payload):
    assessment = Assessment.model_validate(payload)
    expected = prepare_assessment(report, provenance)
    if assessment.input_files != provenance or len(assessment.cases) != 3:
        raise ValueError("La revisión corresponde a otros archivos o está incompleta.")
    dimension_count, claim_count = 0, 0
    for case, original in zip(assessment.cases, expected["cases"], strict=True):
        for key in ("level", "status", "content_review_available", "context"):
            if json.dumps(getattr(case, key), sort_keys=True, allow_nan=False) != json.dumps(
                original[key], sort_keys=True, allow_nan=False
            ):
                raise ValueError("La evidencia de contexto no se modifica al revisar.")
        if str(case.id) != original["id"] or set(case.dimensions) != set(DIMENSIONS):
            raise ValueError("Caso repetido/ajeno o dimensiones incorrectas.")
        if [claim.path for claim in case.claims] != [claim["path"] for claim in original["claims"]]:
            raise ValueError("No se omiten, duplican o inventan afirmaciones.")
        decisions = sum(value.verdict is not None for value in case.dimensions.values())
        if not case.content_review_available and decisions:
            raise ValueError("Sin recurso no hay dimensiones semánticas que calificar.")
        dimension_count += decisions
        for claim, context in zip(case.claims, original["context"]["claims"], strict=True):
            if not set(claim.source_aliases).issubset(context["citations"]):
                raise ValueError("La referencia de revisión no pertenece a esta afirmación.")
            claim_count += claim.support is not None
    if dimension_count + claim_count and assessment.reviewer_name is None:
        raise ValueError("Decisiones sin revisor y fecha declarados.")
    available_dimensions = report["valid_resource_count"] * len(DIMENSIONS)
    available_claims = sum(len(case["claims"]) for case in report["cases"])
    complete = (
        available_dimensions > 0
        and dimension_count == available_dimensions
        and claim_count == available_claims
    )
    return {
        "report_version": "human-review-validation-v1",
        "input_files": provenance,
        "technical_report": copy.deepcopy(report),
        "declared_assessment": assessment.model_dump(mode="json"),
        "semantic_review_status": "available_content_reviewed"
        if complete
        else "partial"
        if dimension_count + claim_count
        else "pending_human",
        "coverage": {
            "assessed_dimensions": dimension_count,
            "available_dimensions": available_dimensions,
            "assessed_claims": claim_count,
            "available_claims": available_claims,
            "cases_without_content": report["failed_case_count"],
        },
        "limitations": [
            "Identidad y decisiones declaradas por quien aporta el archivo; no autenticadas.",
            "Validar el registro no valida sus conclusiones ni otorga aprobación académica.",
            "Revisar contenido disponible no completa casos fallidos ni un benchmark causal.",
        ],
    }


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("Archivo demasiado grande.")
    return raw, json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "apply"))
    parser.add_argument("histories", type=Path, nargs=3, metavar="HISTORY")
    parser.add_argument("output", type=Path, help="Nuevo destino, nunca sobrescribe")
    parser.add_argument("--assessment", type=Path, help="Plantilla rellenada, para apply")
    args = parser.parse_args()
    try:
        if (args.mode == "apply") != (args.assessment is not None):
            raise ValueError("apply requiere revisión; prepare no la admite.")
        rows, provenance = [], []
        for level, path in zip(LEVELS, args.histories, strict=True):
            raw, history = read_json(path)
            rows.append({"level": level, "history": history})
            provenance.append({"level": level, "input_sha256": hashlib.sha256(raw).hexdigest()})
        report = build_trial_review(rows)
        if args.mode == "prepare":
            result = prepare_assessment(report, provenance)
        else:
            raw, payload = read_json(args.assessment)
            result = apply_assessment(report, provenance, payload)
            result["assessment_sha256"] = hashlib.sha256(raw).hexdigest()
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        text.encode("utf-8")
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(text)
    except (OSError, ValueError, TypeError, KeyError, ContentError):
        parser.exit(1, "No se guardó: evidencia/revisión inválida o destino existente.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
