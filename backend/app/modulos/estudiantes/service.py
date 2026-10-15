from fastapi import HTTPException

from app.modulos.estudiantes.schemas import ANSWER_KEYS, PracticeProgress


class PracticeService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, owner, submission):
        if submission.assignment_id is not None:
            assignment = self.repository.assignment(owner, submission.assignment_id)
            if assignment is None:
                raise HTTPException(404, "Actividad no disponible.")
            if assignment.version != submission.version:
                raise HTTPException(409, "El bloque no corresponde a esta actividad.")
            if assignment.status != "open":
                existing = self.repository.attempt(owner, submission.id)
                if (
                    existing is not None
                    and existing.version == submission.version
                    and existing.answers == submission.answers
                    and existing.assignment_id == submission.assignment_id
                ):
                    return existing
                raise HTTPException(
                    409,
                    "La actividad está cerrada o cancelada y no admite nuevos intentos. "
                    "Tus resultados guardados se conservan. Puedes continuar en la práctica libre.",
                )
        score = sum(
            a == b for a, b in zip(submission.answers, ANSWER_KEYS[submission.version], strict=True)
        )
        row = self.repository.save(owner, submission, score)
        if (
            row.version != submission.version
            or row.answers != submission.answers
            or getattr(row, "assignment_id", None) != submission.assignment_id
        ):
            raise HTTPException(409, "Este intento ya se guardó con otras respuestas.")
        return row

    def page(self, owner, offset, limit):
        rows, total, best = self.repository.page(owner, offset, limit)
        return PracticeProgress(
            items=rows, total=total, best_score=best, offset=offset, limit=limit
        )
