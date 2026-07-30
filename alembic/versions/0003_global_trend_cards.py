"""add enriched global trend card fields

Revision ID: 0003_global_trend_cards
Revises: 0002_search_features
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_global_trend_cards"
down_revision = "0002_search_features"
branch_labels = None
depends_on = None


def upgrade():
    # Preserve historical records while moving their names into the new UI
    # taxonomy. The updates are idempotent for a fresh database.
    op.execute("UPDATE categories SET name = 'Finance' WHERE name = 'Business'")
    op.execute("UPDATE categories SET name = 'Entertainment' WHERE name = 'Showbiz'")
    op.execute("UPDATE categories SET name = 'Local' WHERE name = 'Metro/Local'")
    op.execute("UPDATE trending_terms SET category_name = 'Finance' WHERE category_name = 'Business'")
    op.execute("UPDATE trending_terms SET category_name = 'Entertainment' WHERE category_name = 'Showbiz'")
    op.execute("UPDATE trending_terms SET category_name = 'Local' WHERE category_name = 'Metro/Local'")
    op.add_column("trending_terms", sa.Column("scope", sa.String(), nullable=False, server_default="philippines"))
    op.add_column("trending_terms", sa.Column("title", sa.String(), nullable=True))
    op.add_column("trending_terms", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("trending_terms", sa.Column("url", sa.String(), nullable=True))
    op.add_column("trending_terms", sa.Column("ticker", sa.String(), nullable=True))
    op.add_column("trending_terms", sa.Column("relevance_score", sa.Integer(), nullable=True))
    op.create_index("ix_trending_terms_scope_captured_at", "trending_terms", ["scope", "captured_at"])


def downgrade():
    op.drop_index("ix_trending_terms_scope_captured_at", table_name="trending_terms")
    op.drop_column("trending_terms", "relevance_score")
    op.drop_column("trending_terms", "ticker")
    op.drop_column("trending_terms", "url")
    op.drop_column("trending_terms", "summary")
    op.drop_column("trending_terms", "title")
    op.drop_column("trending_terms", "scope")
    op.execute("UPDATE categories SET name = 'Business' WHERE name = 'Finance'")
    op.execute("UPDATE categories SET name = 'Showbiz' WHERE name = 'Entertainment'")
    op.execute("UPDATE categories SET name = 'Metro/Local' WHERE name = 'Local'")
    op.execute("UPDATE trending_terms SET category_name = 'Business' WHERE category_name = 'Finance'")
    op.execute("UPDATE trending_terms SET category_name = 'Showbiz' WHERE category_name = 'Entertainment'")
    op.execute("UPDATE trending_terms SET category_name = 'Metro/Local' WHERE category_name = 'Local'")
