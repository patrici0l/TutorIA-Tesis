import hashlib
import io
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import text
from starlette.datastructures import Headers
from test_ingestion_database import postgres_ingestion as postgres_ingestion

from app.main import create_app
from app.modulos.documentos.models import Document
from app.modulos.rag.models import DocumentChunk
from app.modulos.rag.repositorios.index_repository import IndexRepository
from app.modulos.rag.repositorios.search_repository import SearchRepository
from app.modulos.rag.router import get_search_service
from app.modulos.rag.servicios.embedding_service import EmbeddingService
from app.modulos.rag.servicios.embedding_worker_client import EmbeddingWorkerClient
from app.modulos.rag.servicios.model_spec import EMBEDDING_VERSION, MODEL_ID, MODEL_REVISION
from app.modulos.rag.servicios.query_service import QUERY_VERSION, embedding_query
from app.modulos.rag.servicios.search_service import SearchService
from app.nucleo.dependencias.auth import get_current_user

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DB_TESTS") != "1" or os.getenv("RUN_MODEL_TESTS") != "1",
        reason="Requires migrated PostgreSQL and pinned local model",
    ),
]


def test_reference_retrieval_filters_sources_exact_and_hnsw(postgres_ingestion):
    db, owner, _, documents, chunks, ingest, _ = postgres_ingestion
    dataset = json.loads((Path(__file__).parents[1] / "fixtures/rag_reference.json").read_text())
    model = EmbeddingService(ingest.settings.embedding_model_path)
    vectors, counts = model.encode([entry["text"] for entry in dataset["passages"]])
    baseline_queries, _ = model.encode([entry["text"] for entry in dataset["queries"]], "query")
    queries, _ = model.encode(
        [embedding_query(entry["text"]) for entry in dataset["queries"]], "query"
    )
    repository = SearchRepository(db)
    index = IndexRepository(db)
    keys = {}
    references = {}
    for entry, vector, count in zip(dataset["passages"], vectors, counts, strict=True):
        upload = UploadFile(
            io.BytesIO(entry["text"].encode()),
            filename=f"{entry['key']}.txt",
            headers=Headers({"content-type": "text/plain"}),
        )
        try:
            record = documents.upload(upload, entry["title"], owner.id)
        finally:
            upload.file.close()
        ingest.process(record.id, owner.id)
        token = index.claim(record.id, owner.id)
        snapshot = index.snapshot(record.id)
        assert len(snapshot) == 1
        assert index.publish(
            record.id,
            token,
            [{"id": snapshot[0][0], "embedding": vector, "embedding_tokens": count}],
        )
        keys[snapshot[0][0]] = entry["key"]
        references[snapshot[0][0]] = entry["text"]

    # Ineligible documents share an ideal query vector, so filtering is observable.
    for changes in [
        {"index_status": "failed"},
        {"index_status": "indexing"},
        {"processing_status": "failed"},
        {"embedding_revision": "different"},
        {"embedding_model": "different"},
        {"embedding_version": "different"},
        {"deleted_at": datetime.now(UTC), "status": "deleted"},
        {"owner_id": uuid4()},
    ]:
        values = dict(
            owner_id=owner.id,
            filename="ineligible.txt",
            title="Ineligible synthetic",
            mime_type="text/plain",
            size_bytes=1,
            sha256="0" * 64,
            status="uploaded",
            processing_status="processed",
            processing_version="test",
            index_status="indexed",
            embedding_model=MODEL_ID,
            embedding_revision=MODEL_REVISION,
            embedding_version=EMBEDDING_VERSION,
        )
        # The FK needs a real second user rather than a guessed identifier.
        if "owner_id" in changes:
            from app.modulos.usuarios.models import User

            other = User(
                institutional_email=f"other-{uuid4().hex}@example.org",
                nombre="Otro",
                apellido="Ficticio",
                rol="teacher",
                activo=True,
                last_login=datetime.now(UTC),
            )
            db.add(other)
            db.flush()
            changes["owner_id"] = other.id
        record = Document(**(values | changes))
        db.add(record)
        db.flush()
        source = "Texto sintético ajeno o no elegible."
        db.add(
            DocumentChunk(
                document_id=record.id,
                position=0,
                source_kind="paragraph",
                source_index=1,
                char_start=0,
                char_end=len(source),
                text=source,
                source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                embedding=queries[0],
                embedding_tokens=10,
            )
        )
    db.commit()
    assert repository.count_available(owner.id) == len(keys)
    report_rows = []
    for entry, query, baseline in zip(dataset["queries"], queries, baseline_queries, strict=True):
        baseline_keys = [keys[row["id"]] for row in repository.search(owner.id, baseline, 3, 0)]
        baseline_rank = (
            baseline_keys.index(entry["relevant"]) + 1
            if entry["relevant"] in baseline_keys
            else None
        )
        exact = repository.search(owner.id, query, 3, 0)
        exact_ids = [row["id"] for row in exact]
        assert len(exact_ids) == 3 and set(exact_ids) <= keys.keys()
        assert [row["similarity"] for row in exact] == sorted(
            [row["similarity"] for row in exact], reverse=True
        )
        for row in exact:
            assert row["text"] == references[row["id"]]
            assert row["char_end"] - row["char_start"] == len(row["text"])
            assert row["source_sha256"] == hashlib.sha256(row["text"].encode()).hexdigest()
        # Force and inspect the approximate plan only in this evaluation transaction.
        db.execute(text("SET LOCAL enable_seqscan = off"))
        db.execute(text("SET LOCAL enable_sort = off"))
        db.execute(text("SET LOCAL hnsw.ef_search = 80"))
        db.execute(text("SET LOCAL hnsw.iterative_scan = strict_order"))
        statement = repository.statement(owner.id, query, 3, exact=False)
        compiled = statement.compile(db.bind, compile_kwargs={"literal_binds": True})
        plan = "\n".join(db.scalars(text("EXPLAIN " + str(compiled))))
        assert "ix_fragmentos_embedding_cosine" in plan
        approximate = db.execute(statement).mappings().all()
        ann_ids = [row["id"] for row in approximate]
        assert set(ann_ids) <= keys.keys()
        retrieved = [keys[identifier] for identifier in exact_ids]
        rank = retrieved.index(entry["relevant"]) + 1 if entry["relevant"] in retrieved else None
        report_rows.append(
            {
                "query": entry["text"],
                "embedding_query": embedding_query(entry["text"]),
                "baseline_retrieved": baseline_keys,
                "baseline_rank": baseline_rank,
                "relevant": entry["relevant"],
                "retrieved": retrieved,
                "rank": rank,
                "hnsw_recall_at_3": len(set(ann_ids) & set(exact_ids)) / 3,
            }
        )
        db.execute(text("SET LOCAL enable_seqscan = on"))
        db.execute(text("SET LOCAL enable_sort = on"))
    assert all(row["rank"] for row in report_rows), json.dumps(report_rows, ensure_ascii=False)
    top1 = sum(row["rank"] == 1 for row in report_rows) / len(report_rows)
    assert top1 >= 0.75
    assert all(row["hnsw_recall_at_3"] == 1 for row in report_rows)
    unrelated, _ = model.encode(["¿Cómo preparar una sopa de verduras?"], "query")
    assert repository.search(owner.id, unrelated[0], 3, 0.99) == []
    service = SearchService(repository, EmbeddingWorkerClient(ingest.settings))
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: owner
    app.dependency_overrides[get_search_service] = lambda: service
    with TestClient(app) as client:
        result = client.post(
            "/api/v1/rag/search",
            json={"query": dataset["queries"][0]["text"], "top_k": 3},
            headers={"X-TutorIA-Client": "web"},
        )
        assert result.status_code == 200, result.text
        assert result.json()["results"][0]["document_title"] == "Derivada y tasa de cambio"
        assert result.headers["Cache-Control"] == "no-store"
        assert all("embedding" not in hit for hit in result.json()["results"])
    # Removal is checked against the same repository, with no stale search cache.
    selected = next(
        row
        for row in result.json()["results"]
        if row["document_title"] == "Derivada y tasa de cambio"
    )
    from uuid import UUID

    documents.delete(UUID(selected["document_id"]), owner.id)
    assert repository.count_available(owner.id) == len(keys) - 1
    assert selected["id"] not in [
        str(row["id"]) for row in repository.search(owner.id, queries[0], 10, 0)
    ]
    report = {
        "dataset": dataset["version"],
        "model": MODEL_ID,
        "revision": MODEL_REVISION,
        "embedding_version": EMBEDDING_VERSION,
        "documents": len(keys),
        "queries": len(report_rows),
        "query_version": QUERY_VERSION,
        "baseline_top1_accuracy": sum(row["baseline_rank"] == 1 for row in report_rows)
        / len(report_rows),
        "baseline_recall_at_3": sum(row["baseline_rank"] is not None for row in report_rows)
        / len(report_rows),
        "top1_accuracy": top1,
        "recall_at_3": 1.0,
        "mrr_at_3": float(np.mean([1 / row["rank"] for row in report_rows])),
        "hnsw_recall_at_3": float(np.mean([row["hnsw_recall_at_3"] for row in report_rows])),
        "hnsw_ef_search": 80,
        "hnsw_iterative_scan": "strict_order",
        "results": report_rows,
        "scope": (
            "Synthetic technical verification; not an academic benchmark "
            "or production performance claim."
        ),
    }
    if target := os.getenv("RAG_REPORT_PATH"):
        Path(target).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
