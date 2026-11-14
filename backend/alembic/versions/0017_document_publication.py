"""Require explicit publication before using a document as RAG context."""

import sqlalchemy as sa

from alembic import op

revision = "0017_document_publication"
down_revision = "0016_document_catalog"
branch_labels = None
depends_on = None


def upgrade():
    # Los materiales existentes necesitan revisión; no se publican por migración.
    op.add_column("documentos", sa.Column("published_at", sa.DateTime(timezone=True)))


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT count(*) FROM documentos WHERE published_at IS NOT NULL")
    ):
        raise RuntimeError("Retira las publicaciones antes de revertir esta migración.")
    op.drop_column("documentos", "published_at")
