"""Private prompt/source snapshots before educational generation."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0006_content_trace"
down_revision = "0005_vector_index"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "generaciones_contenido",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("request_snapshot", JSONB(), nullable=False),
        sa.Column("sources_snapshot", JSONB(), nullable=False),
        sa.Column("retrieval_snapshot", JSONB(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("prompt_version", sa.String(40), nullable=False),
        sa.Column("prompt_sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(20)),
        sa.Column("requested_model", sa.String(128)),
        sa.Column("model_version", sa.String(256)),
        sa.Column("response_id", sa.String(256)),
        sa.Column("usage", JSONB(none_as_null=True)),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("estimated_cost", sa.Numeric(18, 8)),
        sa.Column("resource", JSONB(none_as_null=True)),
        sa.Column("error_code", sa.String(40)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status IN ('prepared','succeeded','failed')", name="ck_generaciones_status"
        ),
        sa.CheckConstraint("latency_ms IS NULL OR latency_ms >= 0", name="ck_generaciones_latency"),
        sa.CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0", name="ck_generaciones_cost"
        ),
        sa.CheckConstraint(
            "(status = 'prepared' AND completed_at IS NULL "
            "AND resource IS NULL AND error_code IS NULL) OR "
            "(status = 'succeeded' AND completed_at IS NOT NULL "
            "AND resource IS NOT NULL AND error_code IS NULL) OR "
            "(status = 'failed' AND completed_at IS NOT NULL "
            "AND resource IS NULL AND error_code IS NOT NULL)",
            name="ck_generaciones_terminal",
        ),
    )
    op.create_index("ix_generaciones_contenido_owner_id", "generaciones_contenido", ["owner_id"])


def downgrade():
    op.drop_table("generaciones_contenido")
