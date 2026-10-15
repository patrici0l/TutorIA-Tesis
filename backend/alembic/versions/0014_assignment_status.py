"""Reversible assignment lifecycle, preserving existing attempts."""

import sqlalchemy as sa

from alembic import op

revision = "0014_assignment_status"
down_revision = "0013_practice_assignments"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "asignaciones_practica",
        sa.Column("status", sa.String(12), nullable=False, server_default="open"),
    )
    op.add_column(
        "asignaciones_practica", sa.Column("status_changed_at", sa.DateTime(timezone=True))
    )
    op.create_check_constraint(
        "ck_assignment_status",
        "asignaciones_practica",
        "status IN ('open', 'closed', 'cancelled')",
    )


def downgrade():
    op.drop_constraint("ck_assignment_status", "asignaciones_practica", type_="check")
    op.drop_column("asignaciones_practica", "status_changed_at")
    op.drop_column("asignaciones_practica", "status")
