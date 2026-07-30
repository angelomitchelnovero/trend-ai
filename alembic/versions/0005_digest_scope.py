"""add scope to digests

Revision ID: 0005_digest_scope
Revises: 0004_backfill_ai_trends
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_digest_scope"
down_revision = "0004_backfill_ai_trends"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("digests", sa.Column("scope", sa.String(), nullable=False, server_default="philippines"))
    op.create_index("ix_digests_scope_generated_at", "digests", ["scope", "generated_at"])


def downgrade():
    op.drop_index("ix_digests_scope_generated_at", table_name="digests")
    op.drop_column("digests", "scope")
