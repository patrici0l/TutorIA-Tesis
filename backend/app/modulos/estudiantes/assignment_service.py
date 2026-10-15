from fastapi import HTTPException

from app.modulos.estudiantes.assignment_schemas import AssignmentPage


class AssignmentService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, user, submission):
        if user.rol not in ("teacher", "admin"):
            raise HTTPException(403, "Solo un docente puede asignar actividades.")
        student = self.repository.student(str(submission.student_email))
        if student is None:
            raise HTTPException(
                422,
                "No hay una cuenta de estudiante activa con ese correo. "
                "Debe iniciar sesión antes de recibir actividades.",
            )
        row = self.repository.create(user.id, student.id, submission)
        if (
            row.teacher_id != user.id
            or row.student_id != student.id
            or any(
                getattr(row, key) != getattr(submission, key)
                for key in ("version", "title", "instructions")
            )
        ):
            raise HTTPException(
                409,
                "Esta solicitud ya fue utilizada. Actualiza las actividades antes de crear otra.",
            )
        return self.detail(user, row.id)

    def detail(self, user, identifier):
        row = self.repository.detail(user, identifier)
        if row is None:
            raise HTTPException(404, "Actividad no disponible.")
        return row

    def page(self, user, offset, limit):
        rows, total = self.repository.page(user, offset, limit)
        return AssignmentPage(items=rows, total=total, offset=offset, limit=limit)
