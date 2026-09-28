"""Keep per-fact provenance with stored vectors."""
from alembic import op
import sqlalchemy as sa

revision = "b7248a6c19a1"
down_revision = "8600e675dded"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("chunks", sa.Column("source_ids", sa.Text(), nullable=False, server_default=""))
    op.add_column("chunks", sa.Column("source_titles", sa.Text(), nullable=False, server_default=""))
    op.add_column("chunks", sa.Column("source_urls", sa.Text(), nullable=False, server_default=""))


def downgrade():
    op.drop_column("chunks", "source_urls")
    op.drop_column("chunks", "source_titles")
    op.drop_column("chunks", "source_ids")
