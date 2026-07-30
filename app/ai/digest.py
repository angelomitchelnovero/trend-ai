"""
Daily digest generation — promote this from
experiments/05_digest_check.py once that experiment's output is judged
good enough to show on the dashboard.
"""

import os
import time
from datetime import datetime, timedelta

from google import genai
from google.api_core.exceptions import ResourceExhausted
from sqlalchemy.orm import Session

from app.ai.summarize import MAX_RETRIES_ON_RATE_LIMIT, RATE_LIMIT_RETRY_WAIT
from app.models.schema import Article, Digest, TrendingTerm

DIGEST_PROMPT = """You are writing a short daily "what's trending in the
Philippines" briefing for a news dashboard. Below are today's top story
headlines and summaries from multiple outlets. Write a single cohesive
briefing (150-250 words) that groups related stories, highlights what
matters most, and reads naturally rather than as a bullet dump. Keep a
neutral, informative tone — this is a news digest, not opinion content.

Stories:
{stories}

Daily briefing:"""

GLOBAL_DIGEST_PROMPT = """You are writing a concise daily briefing for a global AI and technology news dashboard.
Use only the facts in the supplied card summaries. Write 100-160 words that connect the most important developments, distinguish AI from broader technology where helpful, and explain why the shifts matter. Stay neutral and do not speculate or add outside knowledge.

Global signals:
{signals}

Global briefing:"""

# gemini-2.5-flash — same model as Philippine summaries; this digest is the
# climactic output of the day, worth the higher-quality bucket.
DIGEST_MODEL = "gemini-2.5-flash"
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _generate(prompt: str) -> str:
    for attempt in range(1, MAX_RETRIES_ON_RATE_LIMIT + 1):
        try:
            response = _get_client().models.generate_content(
                model=DIGEST_MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except ResourceExhausted:
            if attempt == MAX_RETRIES_ON_RATE_LIMIT:
                raise
            print(f"    Rate limited — waiting {RATE_LIMIT_RETRY_WAIT}s (retry {attempt}/{MAX_RETRIES_ON_RATE_LIMIT})...")
            time.sleep(RATE_LIMIT_RETRY_WAIT)
    raise RuntimeError("unreachable")  # loop always returns or raises above


def generate_daily_digest(db: Session, max_stories: int = 8) -> Digest:
    since = datetime.utcnow() - timedelta(days=1)
    articles = (
        db.query(Article)
        .filter(Article.published_at >= since, Article.summary.isnot(None))
        .order_by(Article.published_at.desc())
        .limit(max_stories)
        .all()
    )

    if not articles:
        raise ValueError("No summarized articles in the last 24h to digest")

    stories_block = "\n".join(
        f"[{a.source.name if a.source else 'unknown'}] {a.title} — {a.summary}"
        for a in articles
    )
    prompt = DIGEST_PROMPT.format(stories=stories_block)

    text = _generate(prompt)
    digest = Digest(content=text, scope="philippines")
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest


def generate_global_digest(db: Session, max_signals: int = 8) -> Digest:
    """Create a fact-grounded briefing from the latest enriched AI and Tech cards."""
    signals = (
        db.query(TrendingTerm)
        .filter(
            TrendingTerm.scope == "global",
            TrendingTerm.category_name.in_(("AI", "Tech")),
            TrendingTerm.summary.isnot(None),
        )
        .order_by(TrendingTerm.relevance_score.desc().nullslast(), TrendingTerm.captured_at.desc())
        .limit(max_signals)
        .all()
    )
    if not signals:
        raise ValueError("No enriched global AI or Tech signals available to digest")

    signals_block = "\n".join(
        f"[{signal.category_name}] {signal.title or signal.term} — {signal.summary}"
        for signal in signals
    )
    text = _generate(GLOBAL_DIGEST_PROMPT.format(signals=signals_block))
    digest = Digest(content=text, scope="global")
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest
