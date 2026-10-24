from fastapi import HTTPException

from app.modulos.estudiantes.assignment_schemas import AssignmentPage


class AssignmentService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, user, submission):
        if user.rol not in ("teacher", "admin"):
            raise HTTPException(403, "Solo un docente puede asignar actividades.")
        if submission.resource_id is not None:
            resource = self.repository.resource(user.id, submission.resource_id)
            if resource is None:
                raise HTTPException(404, "Selecciona un recurso propio generado correctamente.")
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
                for key in ("version", "title", "instructions", "resource_id")
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

    def change_status(self, user, identifier, change):
        if user.rol not in ("teacher", "admin"):
            raise HTTPException(403, "Solo un docente puede cambiar el estado de una actividad.")
        row = self.repository.lock_owned(user.id, identifier)
        if row is None:
            raise HTTPException(404, "Actividad no disponible.")
        # Repetir un cambio ya aplicado es seguro; una pantalla desactualizada no lo sobrescribe.
        if row.status != change.status and row.status != change.expected_status:
            raise HTTPException(
                409, "El estado cambió. Actualiza las actividades antes de continuar."
            )
        self.repository.change_status(row, change.status)
        return self.detail(user, identifier)

    def page(self, user, offset, limit):
        rows, total = self.repository.page(user, offset, limit)
        return AssignmentPage(items=rows, total=total, offset=offset, limit=limit)
