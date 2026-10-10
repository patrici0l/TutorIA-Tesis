"""Local reproducible E5 embeddings with cosine HNSW index."""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision = "0005_vector_index"
down_revision = "0004_document_chunks"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "documentos",
        sa.Column("index_status", sa.String(20), nullable=False, server_default="pending"),
    )
    for name in ("index_error", "embedding_revision", "embedding_version"):
        op.add_column("documentos", sa.Column(name, sa.String(40)))
    op.add_column("documentos", sa.Column("index_token", sa.Uuid()))
    for name in ("index_started_at", "indexed_at"):
        op.add_column("documentos", sa.Column(name, sa.DateTime(timezone=True)))
    op.add_column("documentos", sa.Column("embedding_model", sa.String(100)))
    op.create_check_constraint(
        "ck_documentos_index_status",
        "documentos",
        "index_status IN ('pending','indexing','indexed','failed')",
    )
    op.add_column("fragmentos_documento", sa.Column("embedding", Vector(384)))
    op.add_column("fragmentos_documento", sa.Column("embedding_tokens", sa.Integer()))
    op.create_check_constraint(
        "ck_fragmentos_tokens",
        "fragmentos_documento",
        "embedding_tokens IS NULL OR embedding_tokens BETWEEN 1 AND 512",
    )
    op.create_index(
        "ix_fragmentos_embedding_cosine",
        "fragmentos_documento",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade():
    op.drop_index("ix_fragmentos_embedding_cosine", "fragmentos_documento")
    op.drop_constraint("ck_fragmentos_tokens", "fragmentos_documento")
    op.drop_column("fragmentos_documento", "embedding_tokens")
    op.drop_column("fragmentos_documento", "embedding")
    op.drop_constraint("ck_documentos_index_status", "documentos")
    for name in (
        "index_status",
        "index_error",
        "index_token",
        "index_started_at",
        "indexed_at",
        "embedding_model",
        "embedding_revision",
        "embedding_version",
    ):
        op.drop_column("documentos", name)
