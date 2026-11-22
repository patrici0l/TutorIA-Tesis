"""Solicitudes privadas del estudiante sobre corpus explícitamente compartido."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.actividades.repository import AssignmentRepository
from app.modulos.contenidos.access_models import LearningAccess
from app.modulos.contenidos.history_schemas import HistoryDetail, HistoryPage
from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.router import get_generation_service, get_history_service, quota
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.generate_preparation_service import (
    GeneratePreparationService,
    GenerationCommand,
    GenerationResponse,
)
from app.modulos.contenidos.servicios.history_service import HistoryService
from app.modulos.contenidos.servicios.preparation_service import PreparationService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.documentos.models import Document
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.rag.router import get_search_service
from app.modulos.rag.servicios.search_service import SearchService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user, require_client_header
from app.nucleo.dependencias.autorizacion import Owner

router = APIRouter(prefix="/learning", tags=["learning"])
DB = Annotated[Session, Depends(get_session)]


def require_student(user: Annotated[User, Depends(get_current_user)]):
    if user.rol != "student":
        raise HTTPException(403, "Este espacio es para estudiantes.")
    return user


Student = Annotated[User, Depends(require_student)]


class AccessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_email: EmailStr
    course: str = Field(min_length=1, max_length=160)


class StudentRequest(ContentRequest):
    # La materia y el docente se resuelven en servidor a partir del acceso concedido.
    access_id: UUID
    course: None = None


def access_for(db, identifier, student, lock=False):
    statement = (
        select(LearningAccess)
        .join(User, User.id == LearningAccess.teacher_id)
        .where(
            LearningAccess.id == identifier,
            LearningAccess.student_id == student,
            LearningAccess.revoked_at.is_(None),
            User.activo.is_(True),
            User.rol.in_(["teacher", "admin"]),
        )
    )
    if lock:
        statement = statement.with_for_update(of=LearningAccess)
    access = db.scalar(statement)
    if access is None:
        raise HTTPException(403, "No tienes acceso a esta asignatura. Consulta a tu profesor.")
    return access


@router.get("/access")
def teacher_access(user: Owner, db: DB):
    rows = db.execute(
        select(LearningAccess, User.institutional_email)
        .join(User, User.id == LearningAccess.student_id)
        .where(LearningAccess.teacher_id == user.id)
        .order_by(LearningAccess.created_at.desc())
        .limit(500)
    )
    return [
        dict(id=a.id, course=a.course, student_email=email, active=a.revoked_at is None)
        for a, email in rows
    ]


@router.post("/access", status_code=201, dependencies=[Depends(require_client_header)])
def grant(request: AccessRequest, user: Owner, db: DB):
    course = ContentRequest.normalize_course(request.course)
    if not db.scalar(
        select(Document.id)
        .where(
            Document.owner_id == user.id,
            Document.course == course,
            Document.deleted_at.is_(None),
        )
        .limit(1)
    ):
        raise HTTPException(422, "Elige una asignatura de tus documentos.")
    student = AssignmentRepository(db).student(str(request.student_email))
    if student is None:
        raise HTTPException(404, "No se encontró un estudiante activo con ese correo.")
    statement = (
        insert(LearningAccess)
        .values(
            teacher_id=user.id,
            student_id=student.id,
            course=course,
        )
        .on_conflict_do_update(
            index_elements=["teacher_id", "student_id", "course"],
            set_={"revoked_at": None},
        )
        .returning(LearningAccess.id)
    )
    identifier = db.scalar(statement)
    db.commit()
    return {"id": identifier}


@router.delete(
    "/access/{identifier}", status_code=204, dependencies=[Depends(require_client_header)]
)
def revoke(identifier: UUID, user: Owner, db: DB):
    access = db.scalar(
        select(LearningAccess)
        .where(
            LearningAccess.id == identifier,
            LearningAccess.teacher_id == user.id,
        )
        .with_for_update()
    )
    if access is None:
        raise HTTPException(404, "Acceso no disponible.")
    access.revoked_at = datetime.now(UTC)
    db.commit()


@router.get("/courses")
def courses(user: Student, db: DB):
    rows = db.execute(
        select(LearningAccess, User)
        .join(
            User,
            User.id == LearningAccess.teacher_id,
        )
        .where(
            LearningAccess.student_id == user.id,
            LearningAccess.revoked_at.is_(None),
            User.activo.is_(True),
            User.rol.in_(["teacher", "admin"]),
        )
        .order_by(LearningAccess.course, LearningAccess.id)
        .limit(500)
    )
    return [dict(id=a.id, course=a.course, teacher=f"{t.nombre} {t.apellido}") for a, t in rows]


class StudentPreparer(PrepareContentService):
    def __init__(self, search, teacher):
        super().__init__(search, EducationalPromptBuilder())
        self.teacher = teacher

    def prepare(self, request, owner, max_input_chars=12000, adaptation=None):
        return super().prepare(request, self.teacher, max_input_chars)


class StudentRepository(GenerationRepository):
    def __init__(self, db, access_id):
        super().__init__(db)
        self.access_id = access_id

    def prepare(self, owner, prepared, target=None):
        # Revalidar después de la búsqueda: una revocación concurrente impide guardar.
        access_for(self.db, self.access_id, owner, lock=True)
        return super().prepare(owner, prepared, target, learning_access_id=self.access_id)


@router.post(
    "/prepare",
    response_model=PreparationResponse,
    status_code=201,
    dependencies=[Depends(require_client_header)],
)
def prepare(
    request: StudentRequest,
    user: Student,
    db: DB,
    search: Annotated[SearchService, Depends(get_search_service)],
):
    access = access_for(db, request.access_id, user.id)
    content = ContentRequest.model_validate(
        {
            **request.model_dump(exclude={"access_id", "course"}),
            "course": access.course,
        }
    )
    service = PreparationService(
        StudentPreparer(search, access.teacher_id),
        StudentRepository(db, access.id),
        get_settings().llm_max_input_chars,
    )
    try:
        return service.prepare(content, user.id)
    except HTTPException as error:
        if error.status_code == 422 and "fuentes" in str(error.detail):
            raise HTTPException(
                422,
                "Tu profesor debe habilitar materiales de esta asignatura "
                "antes de que puedas solicitar contenido.",
            ) from None
        raise


@router.get("/quota")
def student_quota(user: Student, db: DB):
    return quota(user, db, get_settings())


@router.get("/history", response_model=HistoryPage)
def history(
    user: Student,
    service: Annotated[HistoryService, Depends(get_history_service)],
    offset: Annotated[int, Query(ge=0, le=100000)] = 0,
):
    return service.page(user.id, offset, 10)


@router.get("/history/{identifier}", response_model=HistoryDetail)
def detail(
    identifier: UUID,
    user: Student,
    service: Annotated[HistoryService, Depends(get_history_service)],
):
    return service.detail(identifier, user.id)


@router.post(
    "/{identifier}/generate",
    response_model=GenerationResponse,
    dependencies=[Depends(require_client_header)],
)
def generate(
    identifier: UUID,
    user: Student,
    service: Annotated[GeneratePreparationService, Depends(get_generation_service)],
    command: GenerationCommand = GenerationCommand(),
):
    return service.generate(identifier, user.id)
