"""Add local course, provenance and immutable document revision links."""

import sqlalchemy as sa

from alembic import op

revision = "0016_document_catalog"
down_revision = "0015_resource_assignments"
branch_labels = None
depends_on = None


def upgrade():
    # Legacy rows remain unclassified; never invent authorization for existing material.
    for name, length in [("course", 160), ("source_reference", 500), ("permission_note", 500)]:
        op.add_column("documentos", sa.Column(name, sa.String(length), nullable=True))
    op.add_column("documentos", sa.Column("permission_recorded_at", sa.DateTime(timezone=True)))
    op.add_column(
        "documentos", sa.Column("version_number", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("documentos", sa.Column("previous_version_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_document_previous", "documentos", "documentos", ["previous_version_id"], ["id"]
    )
    op.create_unique_constraint("uq_document_previous", "documentos", ["previous_version_id"])
    op.create_index("ix_documentos_course", "documentos", ["course"])


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT count(*) FROM documentos WHERE course IS NOT NULL")):
        raise RuntimeError(
            "Existen metadatos documentales: no se permite descartarlos silenciosamente."
        )
    op.drop_index("ix_documentos_course", table_name="documentos")
    op.drop_constraint("uq_document_previous", "documentos", type_="unique")
    op.drop_constraint("fk_document_previous", "documentos", type_="foreignkey")
    for name in [
        "previous_version_id",
        "version_number",
        "permission_recorded_at",
        "permission_note",
        "source_reference",
        "course",
    ]:
        op.drop_column("documentos", name)
