from uuid import uuid4

from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.rag.schemas import SearchHit, SearchResponse


def request(kind="EXPLANATION", **values):
    fields = dict(
        topic="Derivadas", learning_objective="Comprender la tasa de cambio", resource_type=kind
    )
    if kind == "FEEDBACK":
        fields["student_answer"] = "Respuesta sintética del estudiante."
    fields.update(values)
    return ContentRequest(**fields)


def retrieval(text="La derivada mide la tasa de cambio instantánea."):
    return SearchResponse(
        query="Derivadas",
        embedding_query="Derivadas",
        query_version="calculo-alias-v1",
        top_k=3,
        min_similarity=0,
        available_chunks=1,
        elapsed_ms=1,
        embedding_model="modelo-local-sintetico",
        embedding_revision="rev-test",
        embedding_version="test-v1",
        results=[
            SearchHit(
                id=uuid4(),
                document_id=uuid4(),
                document_title="Fuente sintética",
                filename="sintetico.txt",
                document_sha256="a" * 64,
                source_sha256="b" * 64,
                processing_version="test-v1",
                similarity=0.8,
                position=0,
                source_kind="paragraph",
                source_index=1,
                char_start=0,
                char_end=len(text),
                text=text,
            )
        ],
    )


def cited(text="Texto sintético para probar el contrato."):
    return {"text": text, "citations": ["S1"]}


def resource(kind="EXPLANATION"):
    values = dict(resource_type=kind, title="Recurso sintético de prueba")
    if kind == "EXPLANATION":
        values.update(summary=cited(), steps=[cited()], worked_example=cited())
    elif kind == "EXERCISE":
        values.update(statement=cited(), hints=[cited()], solution_steps=[cited()], answer=cited())
    elif kind == "QUIZ":
        values["questions"] = [
            dict(
                statement=cited(),
                options=["A", "B", "C", "D"],
                correct_option=0,
                explanation=cited(),
            )
            for _ in range(3)
        ]
    else:
        values.update(diagnosis=cited(), correction=cited(), next_step=cited())
    return values
