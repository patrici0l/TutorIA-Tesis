"""Allow assigning a successfully generated educational resource."""

import sqlalchemy as sa

from alembic import op

revision = "0015_resource_assignments"
down_revision = "0014_assignment_status"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("asignaciones_practica", sa.Column("resource_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_assignment_resource",
        "asignaciones_practica",
        "generaciones_contenido",
        ["resource_id"],
        ["id"],
    )
    op.create_check_constraint(
        "ck_assignment_resource",
        "asignaciones_practica",
        "(version = 'resource-v1') = (resource_id IS NOT NULL)",
    )


def downgrade():
    # Refuse to discard assigned material silently.
    connection = op.get_bind()
    if connection.scalar(
        sa.text("SELECT count(*) FROM asignaciones_practica WHERE resource_id IS NOT NULL")
    ):
        raise RuntimeError("Existen recursos asignados; respáldalos antes de revertir.")
    op.drop_constraint("ck_assignment_resource", "asignaciones_practica", type_="check")
    op.drop_constraint("fk_assignment_resource", "asignaciones_practica", type_="foreignkey")
    op.drop_column("asignaciones_practica", "resource_id")
