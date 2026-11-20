"""Conteo compartido para no duplicar el presupuesto entre web e integración."""

from datetime import timedelta

from sqlalchemy import func, select, update

from app.modulos.contenidos.models import ContentGeneration
from app.modulos.integracion_adaptia.models import AdaptiaGeneration


def started_generations(db, since):
    return sum(
        db.scalar(
            select(func.count()).select_from(model).where(model.generation_started_at >= since)
        )
        for model in (ContentGeneration, AdaptiaGeneration)
    )


def active_generations(db):
    return sum(
        db.scalar(select(func.count()).select_from(model).where(model.status == "generating"))
        for model in (ContentGeneration, AdaptiaGeneration)
    )


def expire_interrupted(db, now):
    for model in (ContentGeneration, AdaptiaGeneration):
        db.execute(
            update(model)
            .where(
                model.status == "generating",
                model.generation_started_at < now - timedelta(seconds=90),
            )
            .values(status="failed", error_code="generation_interrupted", completed_at=now)
        )
