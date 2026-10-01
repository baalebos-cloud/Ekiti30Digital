"""support approved Ask Ekiti documents

Revision ID: a4e9c2f1d7b0
Revises: 6fbd4fdce746
Create Date: 2026-10-01
"""

from alembic import op
import sqlalchemy as sa


revision = "a4e9c2f1d7b0"
down_revision = "6fbd4fdce746"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "knowledge_documents",
        "last_verified",
        existing_type=sa.Date(),
        nullable=True,
    )

    op.add_column(
        "knowledge_documents",
        sa.Column(
            "evidence_status",
            sa.String(),
            nullable=False,
            server_default="verified",
        ),
    )

    op.add_column(
        "knowledge_documents",
        sa.Column(
            "ask_ekiti_approved",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "knowledge_documents",
        sa.Column(
            "ask_ekiti_approved_by",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "knowledge_documents",
        sa.Column(
            "ask_ekiti_approved_date",
            sa.Date(),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("knowledge_documents", "ask_ekiti_approved_date")
    op.drop_column("knowledge_documents", "ask_ekiti_approved_by")
    op.drop_column("knowledge_documents", "ask_ekiti_approved")
    op.drop_column("knowledge_documents", "evidence_status")

    op.alter_column(
        "knowledge_documents",
        "last_verified",
        existing_type=sa.Date(),
        nullable=False,
    )
