# Persiste intentos propios e identifica reenvíos por su UUID.
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.modulos.actividades.models import PracticeAssignment
from app.modulos.practica.models import PracticeAttempt


class PracticeRepository:
    def __init__(self, db):
        self.db = db

    def save(self, owner, submission, score):
        self.db.execute(
            insert(PracticeAttempt)
            .values(owner_id=owner, **submission.model_dump(), score=score)
            .on_conflict_do_nothing(index_elements=["owner_id", "id"])
        )
        row = self.db.scalar(
            select(PracticeAttempt).where(
                PracticeAttempt.owner_id == owner, PracticeAttempt.id == submission.id
            )
        )
        # Un reintento idéntico devuelve el original; nunca modifica respuestas previas.
        self.db.commit()
        return row

    def assignment(self, owner, identifier):
        return self.db.scalar(
            select(PracticeAssignment)
            .where(PracticeAssignment.id == identifier, PracticeAssignment.student_id == owner)
            # Serializa el guardado con el cierre/reactivación docente hasta commit.
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def attempt(self, owner, identifier):
        return self.db.get(PracticeAttempt, (owner, identifier))

    def page(self, owner, offset, limit):
        query = select(PracticeAttempt).where(PracticeAttempt.owner_id == owner)
        rows = self.db.scalars(
            query.order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        total, best = self.db.execute(
            select(func.count(), func.max(PracticeAttempt.score)).where(
                PracticeAttempt.owner_id == owner
            )
        ).one()
        return rows, total, best
