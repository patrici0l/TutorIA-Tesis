"""Corpus docente privado, previo a ingesta."""

import sqlalchemy as sa

from alembic import op

revision = "0003_documents"
down_revision = "0002_authentication"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "documentos",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("filename", sa.String(180), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="ck_documentos_size"),
        sa.CheckConstraint("status IN ('uploaded', 'deleted')", name="ck_documentos_status"),
    )
    op.create_index("ix_documentos_owner_id", "documentos", ["owner_id"])


def downgrade():
    op.drop_table("documentos")
