"""Teacher assignments, preserving private unassigned attempts."""

import sqlalchemy as sa

from alembic import op

revision = "0013_practice_assignments"
down_revision = "0012_practice_attempts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "asignaciones_practica",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("teacher_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("version", sa.String(40), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("instructions", sa.String(2000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("id", "student_id", "version", name="uq_assignment_student_version"),
    )
    op.create_index("ix_asignaciones_practica_teacher_id", "asignaciones_practica", ["teacher_id"])
    op.create_index("ix_asignaciones_practica_student_id", "asignaciones_practica", ["student_id"])
    op.add_column("intentos_practica", sa.Column("assignment_id", sa.Uuid(), nullable=True))
    op.create_index("ix_intentos_practica_assignment_id", "intentos_practica", ["assignment_id"])
    op.create_foreign_key(
        "fk_attempt_assignment_student",
        "intentos_practica",
        "asignaciones_practica",
        ["assignment_id", "owner_id", "version"],
        ["id", "student_id", "version"],
    )


def downgrade():
    op.drop_constraint("fk_attempt_assignment_student", "intentos_practica", type_="foreignkey")
    op.drop_index("ix_intentos_practica_assignment_id", table_name="intentos_practica")
    op.drop_column("intentos_practica", "assignment_id")
    op.drop_table("asignaciones_practica")
