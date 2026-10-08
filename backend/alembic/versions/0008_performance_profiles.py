"""Immutable synthetic performance snapshots."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0008_performance_profiles"
down_revision = "0007_generation_claim"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "perfiles_rendimiento",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("schema_version", sa.String(40), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("jsonb_typeof(payload) = 'object'", name="ck_perfiles_payload"),
        sa.CheckConstraint("schema_version = 'performance-profile-v1'", name="ck_perfiles_version"),
    )
    op.create_index("ix_perfiles_rendimiento_owner_id", "perfiles_rendimiento", ["owner_id"])


def downgrade():
    op.drop_index("ix_perfiles_rendimiento_owner_id", "perfiles_rendimiento")
    op.drop_table("perfiles_rendimiento")
