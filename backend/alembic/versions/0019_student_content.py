"""Acceso por estudiante, docente y asignatura; trazabilidad de solicitudes."""

import sqlalchemy as sa

from alembic import op

revision = "0019_student_content"
down_revision = "0018_external_sources"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accesos_aprendizaje",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("teacher_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("course", sa.String(160), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("teacher_id", "student_id", "course"),
    )
    op.create_index("ix_accesos_aprendizaje_teacher_id", "accesos_aprendizaje", ["teacher_id"])
    op.create_index("ix_accesos_aprendizaje_student_id", "accesos_aprendizaje", ["student_id"])
    op.add_column(
        "generaciones_contenido",
        sa.Column("learning_access_id", sa.Uuid(), sa.ForeignKey("accesos_aprendizaje.id")),
    )


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS (SELECT 1 FROM accesos_aprendizaje)")):
        raise RuntimeError("Hay accesos de estudiantes; no se eliminará su trazabilidad.")
    op.drop_column("generaciones_contenido", "learning_access_id")
    op.drop_table("accesos_aprendizaje")
