"""Private completed attempts for the introductory practice bank."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0012_practice_attempts"
down_revision = "0011_execution_configuration"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "intentos_practica",
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), primary_key=True),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("version", sa.String(40), nullable=False),
        sa.Column("answers", postgresql.JSONB(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("score >= 0 AND score <= 3", name="ck_practica_score"),
        sa.CheckConstraint("jsonb_array_length(answers) = 3", name="ck_practica_answers"),
    )


def downgrade():
    op.drop_table("intentos_practica")
