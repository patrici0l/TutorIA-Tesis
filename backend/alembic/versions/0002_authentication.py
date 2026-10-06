"""Usuarios institucionales sin contraseñas y sesiones SSO."""

import sqlalchemy as sa

from alembic import op

revision = "0002_authentication"
down_revision = "0001_enable_vector"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("institutional_email", sa.String(254), nullable=False, unique=True),
        sa.Column("institutional_id", sa.String(255), unique=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellido", sa.String(100), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rol IN ('student', 'teacher', 'admin')", name="ck_usuarios_rol"),
    )
    op.create_table(
        "sesiones_autenticacion",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("mode", sa.String(10), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sesiones_autenticacion_user_id", "sesiones_autenticacion", ["user_id"])
    op.create_table(
        "intentos_sso",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column("mode", sa.String(10), nullable=False),
        sa.Column("service_url", sa.String(2048), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("intentos_sso")
    op.drop_table("sesiones_autenticacion")
    op.drop_table("usuarios")
