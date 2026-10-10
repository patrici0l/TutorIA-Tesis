"""Preserve the conditional cost basis without backfilling historical estimates."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0010_cost_basis"
down_revision = "0009_content_adaptation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "generaciones_contenido",
        sa.Column("cost_basis", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_generaciones_cost_basis",
        "generaciones_contenido",
        "cost_basis IS NULL OR jsonb_typeof(cost_basis) = 'object'",
    )


def downgrade():
    op.drop_constraint("ck_generaciones_cost_basis", "generaciones_contenido", type_="check")
    op.drop_column("generaciones_contenido", "cost_basis")
