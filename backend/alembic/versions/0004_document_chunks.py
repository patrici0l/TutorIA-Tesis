"""Traceable extraction and document chunks; no embeddings yet."""

import sqlalchemy as sa

from alembic import op

revision = "0004_document_chunks"
down_revision = "0003_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "documentos",
        sa.Column("processing_status", sa.String(20), nullable=False, server_default="pending"),
    )
    op.add_column("documentos", sa.Column("processing_error", sa.String(40)))
    op.add_column("documentos", sa.Column("processing_token", sa.Uuid()))
    op.add_column("documentos", sa.Column("processing_started_at", sa.DateTime(timezone=True)))
    op.add_column("documentos", sa.Column("processed_at", sa.DateTime(timezone=True)))
    op.add_column("documentos", sa.Column("processing_version", sa.String(40)))
    op.add_column("documentos", sa.Column("chunk_chars", sa.Integer()))
    op.add_column("documentos", sa.Column("chunk_overlap", sa.Integer()))
    op.add_column(
        "documentos", sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "documentos", sa.Column("text_chars", sa.Integer(), nullable=False, server_default="0")
    )
    op.create_check_constraint(
        "ck_documentos_processing",
        "documentos",
        "processing_status IN ('pending', 'processing', 'processed', 'failed')",
    )
    op.create_check_constraint(
        "ck_documentos_chunk_counts", "documentos", "chunk_count >= 0 AND text_chars >= 0"
    )
    op.create_table(
        "fragmentos_documento",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Uuid(),
            sa.ForeignKey("documentos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("source_kind", sa.String(12), nullable=False),
        sa.Column("source_index", sa.Integer(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_sha256", sa.String(64), nullable=False),
        sa.UniqueConstraint("document_id", "position", name="uq_fragmentos_documento_position"),
        sa.CheckConstraint("source_kind IN ('page', 'paragraph')", name="ck_fragmentos_source"),
        sa.CheckConstraint("source_index > 0 AND position >= 0", name="ck_fragmentos_position"),
        sa.CheckConstraint(
            "char_start >= 0 AND char_end > char_start", name="ck_fragmentos_offsets"
        ),
        sa.CheckConstraint("length(text) = char_end - char_start", name="ck_fragmentos_length"),
    )
    op.create_index("ix_fragmentos_documento_document_id", "fragmentos_documento", ["document_id"])


def downgrade():
    op.drop_table("fragmentos_documento")
    op.drop_constraint("ck_documentos_chunk_counts", "documentos")
    op.drop_constraint("ck_documentos_processing", "documentos")
    for column in (
        "text_chars",
        "chunk_count",
        "chunk_overlap",
        "chunk_chars",
        "processing_version",
        "processed_at",
        "processing_started_at",
        "processing_token",
        "processing_error",
        "processing_status",
    ):
        op.drop_column("documentos", column)
