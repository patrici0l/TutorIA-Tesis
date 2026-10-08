"""Preserve profile and policy used to prepare a resource."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0009_content_adaptation"
down_revision = "0008_performance_profiles"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "generaciones_contenido",
        sa.Column("adaptation_snapshot", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_generaciones_adaptation",
        "generaciones_contenido",
        "adaptation_snapshot IS NULL OR jsonb_typeof(adaptation_snapshot) = 'object'",
    )


def downgrade():
    op.drop_constraint("ck_generaciones_adaptation", "generaciones_contenido", type_="check")
    op.drop_column("generaciones_contenido", "adaptation_snapshot")
