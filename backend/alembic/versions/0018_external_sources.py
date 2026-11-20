"""Preserve provenance of imported external sources without classifying old uploads."""
import sqlalchemy as sa

from alembic import op

revision = "0018_external_sources"
down_revision = "0017_document_publication"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("documentos", sa.Column("external_source", sa.JSON(), nullable=True))


def downgrade():
    if op.get_bind().scalar(sa.text(
        "SELECT count(*) FROM documentos WHERE external_source IS NOT NULL"
    )):
        raise RuntimeError("Conserva la procedencia externa; no se puede revertir con importaciones.")
    op.drop_column("documentos", "external_source")
