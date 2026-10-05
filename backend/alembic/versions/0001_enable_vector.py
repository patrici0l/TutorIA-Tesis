"""Habilita pgvector mediante una migración versionada."""

from alembic import op

revision = "0001_enable_vector"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade():
    # Sin CASCADE: no eliminar tablas o índices dependientes accidentalmente.
    op.execute("DROP EXTENSION IF EXISTS vector")
