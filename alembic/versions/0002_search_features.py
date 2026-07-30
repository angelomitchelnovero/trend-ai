"""add categories to trending terms, presence heartbeats

Revision ID: 0002_search_features
Revises: 0001_initial
Create Date: 2026-07-25

Adds:
- trending_terms.category_name (shared category system with articles)
- trending_terms.previous_score (velocity groundwork)
- presence_heartbeats table (live viewer count)
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_search_features"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("trending_terms", sa.Column("category_name", sa.String(), nullable=True))
    op.add_column("trending_terms", sa.Column("previous_score", sa.Integer(), nullable=True))

    op.create_table(
        "presence_heartbeats",
        sa.Column("session_id", sa.String, primary_key=True),
        sa.Column("last_seen", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("presence_heartbeats")
    op.drop_column("trending_terms", "previous_score")
    op.drop_column("trending_terms", "category_name")
