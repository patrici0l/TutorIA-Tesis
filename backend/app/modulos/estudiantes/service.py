from fastapi import HTTPException

from app.modulos.estudiantes.schemas import CORRECT_OPTIONS, PracticeProgress


class PracticeService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, owner, submission):
        score = sum(a == b for a, b in zip(submission.answers, CORRECT_OPTIONS, strict=True))
        row = self.repository.save(owner, submission, score)
        if row.version != submission.version or row.answers != submission.answers:
            raise HTTPException(409, "Este intento ya se guardó con otras respuestas.")
        return row

    def page(self, owner, offset, limit):
        rows, total, best = self.repository.page(owner, offset, limit)
        return PracticeProgress(
            items=rows, total=total, best_score=best, offset=offset, limit=limit
        )
