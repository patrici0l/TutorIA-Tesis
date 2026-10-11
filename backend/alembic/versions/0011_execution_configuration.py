"""Preserve configured limits at reservation without reconstructing history."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0011_execution_configuration"
down_revision = "0010_cost_basis"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "generaciones_contenido",
        sa.Column("execution_configuration", postgresql.JSONB(), nullable=True),
    )
    op.create_check_constraint(
        "ck_generaciones_execution_configuration",
        "generaciones_contenido",
        "execution_configuration IS NULL OR jsonb_typeof(execution_configuration) = 'object'",
    )


def downgrade():
    op.drop_constraint(
        "ck_generaciones_execution_configuration", "generaciones_contenido", type_="check"
    )
    op.drop_column("generaciones_contenido", "execution_configuration")
