"""Trazabilidad e idempotencia de solicitudes de servicio ADAPTIA."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0018_adaptia_integration"
down_revision = "0017_document_publication"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "generaciones_adaptia",
        sa.Column("request_id", sa.String(128), primary_key=True),
        sa.Column("payload_sha256", sa.String(64), nullable=False),
        sa.Column("request_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("student_id_hash", sa.String(128), nullable=False),
        sa.Column("session_id", sa.String(128), nullable=False),
        sa.Column("prompt_version", sa.String(40), nullable=False),
        sa.Column("prompt_sha256", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("requested_model", sa.String(128), nullable=False),
        sa.Column("usage", postgresql.JSONB(none_as_null=True)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("response", postgresql.JSONB(none_as_null=True)),
        sa.Column("error_code", sa.String(40)),
        sa.Column(
            "generation_started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status IN ('generating','succeeded','failed')", name="ck_adaptia_status"
        ),
        sa.CheckConstraint(
            "(status = 'generating' AND completed_at IS NULL AND response IS NULL "
            "AND error_code IS NULL) OR "
            "(status = 'succeeded' AND completed_at IS NOT NULL AND response IS NOT NULL "
            "AND error_code IS NULL) OR "
            "(status = 'failed' AND completed_at IS NOT NULL AND response IS NULL "
            "AND error_code IS NOT NULL)",
            name="ck_adaptia_terminal",
        ),
    )
    op.create_index(
        "ix_generaciones_adaptia_generation_started_at",
        "generaciones_adaptia",
        ["generation_started_at"],
    )


def downgrade():
    op.drop_index("ix_generaciones_adaptia_generation_started_at", "generaciones_adaptia")
    op.drop_table("generaciones_adaptia")
