"""Durable claim and global generation quota."""

import sqlalchemy as sa

from alembic import op

revision = "0007_generation_claim"
down_revision = "0006_content_trace"
branch_labels = None
depends_on = None


def constraints(generating):
    states = (
        "'prepared','generating','succeeded','failed'"
        if generating
        else "'prepared','succeeded','failed'"
    )
    pending = "status IN ('prepared','generating')" if generating else "status = 'prepared'"
    op.create_check_constraint(
        "ck_generaciones_status", "generaciones_contenido", f"status IN ({states})"
    )
    op.create_check_constraint(
        "ck_generaciones_terminal",
        "generaciones_contenido",
        f"({pending} AND completed_at IS NULL AND resource IS NULL AND error_code IS NULL) OR "
        "(status = 'succeeded' AND completed_at IS NOT NULL "
        "AND resource IS NOT NULL AND error_code IS NULL) OR "
        "(status = 'failed' AND completed_at IS NOT NULL "
        "AND resource IS NULL AND error_code IS NOT NULL)",
    )


def upgrade():
    op.drop_constraint("ck_generaciones_status", "generaciones_contenido")
    op.drop_constraint("ck_generaciones_terminal", "generaciones_contenido")
    op.add_column(
        "generaciones_contenido", sa.Column("generation_started_at", sa.DateTime(timezone=True))
    )
    op.create_index(
        "ix_generaciones_contenido_generation_started_at",
        "generaciones_contenido",
        ["generation_started_at"],
    )
    constraints(True)


def downgrade():
    op.execute(
        "UPDATE generaciones_contenido SET status='failed',"
        "error_code='generation_interrupted',completed_at=now() WHERE status='generating'"
    )
    op.drop_constraint("ck_generaciones_status", "generaciones_contenido")
    op.drop_constraint("ck_generaciones_terminal", "generaciones_contenido")
    op.drop_index("ix_generaciones_contenido_generation_started_at", "generaciones_contenido")
    op.drop_column("generaciones_contenido", "generation_started_at")
    constraints(False)
