"""Prueba manual RAG/IA limitada a la muestra sintética conocida de derivadas."""

import argparse
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base_datos.session import get_engine
from app.configuracion.settings import get_settings
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.generate_content_service import GenerateContentService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.documentos.models import Document
from app.modulos.proveedores_ia.schemas import GenerationTarget
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.rag.router import get_search_service
from app.modulos.usuarios.models import User

DOCUMENT_ID = UUID("84ed0928-238d-46ec-9de2-8f704249ddc3")
DOCUMENT_HASH = "8a281568815d0381a75a66fe4004806aa424a520cb8f6b145eeda104e5f08789"


class SyntheticPreparer(PrepareContentService):
    def prepare(self, *args, **kwargs):
        prepared = super().prepare(*args, **kwargs)
        sources = json.loads(prepared.sources_json)
        if not sources or any(
            source["document_id"] != str(DOCUMENT_ID) or source["document_sha256"] != DOCUMENT_HASH
            for source in sources
        ):
            raise RuntimeError("La prueba solo permite la muestra sintética conocida.")
        return prepared


def main() -> int:
    parser = argparse.ArgumentParser(description="Una generación RAG sintética sin reintentos.")
    parser.add_argument("--free-tier-confirmed", action="store_true", required=True)
    parser.parse_args()
    settings = get_settings().model_copy(
        update={
            "llm_enabled": True,
            "llm_default_provider": "gemini",
            "llm_model": "gemini-3.1-flash-lite",
            "llm_max_output_tokens": 512,
            "llm_requests_per_minute": 1,
            "llm_timeout_seconds": 30,
        }
    )
    with Session(get_engine(), expire_on_commit=False) as db:
        owner = db.execute(
            select(User.id)
            .join(Document, Document.owner_id == User.id)
            .where(
                Document.id == DOCUMENT_ID,
                Document.sha256 == DOCUMENT_HASH,
                Document.deleted_at.is_(None),
                User.activo.is_(True),
                User.rol.in_(["teacher", "admin"]),
            )
        ).scalar_one()
        db.commit()
        service = GenerateContentService(
            SyntheticPreparer(get_search_service(db), EducationalPromptBuilder()),
            GenerationRepository(db),
            create_provider(settings),
            GenerationTarget(provider="gemini", requested_model=settings.llm_model),
            settings.llm_max_input_chars,
        )
        result = service.generate(
            ContentRequest(
                topic="Derivada de x²",
                learning_objective="Reconocer la derivada de x² y su tasa de cambio instantánea.",
                resource_type="EXPLANATION",
            ),
            owner,
        )
        print(
            json.dumps(
                {
                    "id": str(result.id),
                    "status": "succeeded" if result.resource else "failed",
                    "error_code": result.error_code,
                    "resource_type": result.resource.resource_type if result.resource else None,
                }
            )
        )
        return 0 if result.resource else 1


if __name__ == "__main__":
    raise SystemExit(main())
