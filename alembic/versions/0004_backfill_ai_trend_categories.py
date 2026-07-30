"""backfill AI labels for previously ingested global trend cards

Revision ID: 0004_backfill_ai_trends
Revises: 0003_global_trend_cards
"""

from alembic import op

revision = "0004_backfill_ai_trends"
down_revision = "0003_global_trend_cards"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        UPDATE trending_terms
        SET category_name = 'AI'
        WHERE scope = 'global'
          AND (term ILIKE '%artificial intelligence%'
            OR term ILIKE '% AI %'
            OR term ILIKE '%robot%'
            OR term ILIKE '%OpenAI%'
            OR term ILIKE '%Anthropic%'
            OR term ILIKE '%ChatGPT%'
            OR term ILIKE '%Gemini%')
    """)


def downgrade():
    # Category assignment is heuristic; do not guess a prior category on rollback.
    pass
