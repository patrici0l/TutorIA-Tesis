from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.modulos.estudiantes.models import PracticeAssignment, PracticeAttempt
from app.modulos.usuarios.models import User


class AssignmentRepository:
    def __init__(self, db):
        self.db = db

    def student(self, email):
        return self.db.scalar(
            select(User).where(
                func.lower(User.institutional_email) == email.lower(),
                User.rol == "student",
                User.activo.is_(True),
            )
        )

    def create(self, teacher, student, submission):
        values = submission.model_dump(exclude={"student_email"})
        self.db.execute(
            insert(PracticeAssignment)
            .values(**values, teacher_id=teacher, student_id=student)
            .on_conflict_do_nothing(index_elements=["id"])
        )
        row = self.db.get(PracticeAssignment, submission.id)
        self.db.commit()
        return row

    def scope(self, user):
        return (
            PracticeAssignment.student_id == user.id
            if user.rol == "student"
            else PracticeAssignment.teacher_id == user.id
        )

    def query(self, user):
        attempts = (
            select(func.count())
            .where(PracticeAttempt.assignment_id == PracticeAssignment.id)
            .scalar_subquery()
        )
        best = (
            select(func.max(PracticeAttempt.score))
            .where(PracticeAttempt.assignment_id == PracticeAssignment.id)
            .scalar_subquery()
        )
        return (
            select(
                PracticeAssignment.id,
                PracticeAssignment.version,
                PracticeAssignment.title,
                PracticeAssignment.instructions,
                PracticeAssignment.created_at,
                User.institutional_email.label("student_email"),
                attempts.label("attempts"),
                best.label("best_score"),
            )
            .join(User, User.id == PracticeAssignment.student_id)
            .where(self.scope(user))
        )

    def detail(self, user, identifier):
        return (
            self.db.execute(self.query(user).where(PracticeAssignment.id == identifier))
            .mappings()
            .first()
        )

    def page(self, user, offset, limit):
        rows = (
            self.db.execute(
                self.query(user)
                .order_by(PracticeAssignment.created_at.desc(), PracticeAssignment.id.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        total = self.db.scalar(
            select(func.count()).select_from(PracticeAssignment).where(self.scope(user))
        )
        return rows, total
