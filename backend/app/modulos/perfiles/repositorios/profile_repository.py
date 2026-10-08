from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.perfiles.models import PerformanceProfile
from app.modulos.perfiles.schemas import ProfileRequest


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, request: ProfileRequest, owner: UUID):
        record = PerformanceProfile(
            owner_id=owner, payload=request.model_dump(mode="json", exclude_none=True)
        )
        self.db.add(record)
        self.db.flush()
        self.db.commit()
        self.db.refresh(record)
        return record

    def owned(self, identifier: UUID, owner: UUID):
        return self.db.scalar(
            select(PerformanceProfile).where(
                PerformanceProfile.id == identifier, PerformanceProfile.owner_id == owner
            )
        )

    def page(self, owner: UUID, offset: int, limit: int):
        rows = (
            self.db.execute(
                select(
                    PerformanceProfile.id,
                    PerformanceProfile.created_at,
                    PerformanceProfile.payload["student_id"].as_string().label("student_id"),
                    PerformanceProfile.payload["topic"].as_string().label("topic"),
                    PerformanceProfile.payload["performance"].as_float().label("performance"),
                    PerformanceProfile.payload["mastery_level"].as_string().label("mastery_level"),
                )
                .where(PerformanceProfile.owner_id == owner)
                .order_by(PerformanceProfile.created_at.desc(), PerformanceProfile.id.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        total = self.db.scalar(
            select(func.count())
            .select_from(PerformanceProfile)
            .where(PerformanceProfile.owner_id == owner)
        )
        return rows, total
