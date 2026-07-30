"""
Daily digest generation — promote this from
experiments/05_digest_check.py once that experiment's output is judged
good enough to show on the dashboard.
"""

import os
from datetime import datetime, timedelta

import google.generativeai as genai
from sqlalchemy.orm import Session

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

_model = None


def _get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        # gemini-1.5-flash was fully shut down by Google — 1.5 models all 404 now.
        # If gemini-2.5-flash also 404s in the future, check current model names at
        # https://ai.google.dev/gemini-api/docs/models
        _model = genai.GenerativeModel("gemini-2.5-flash")
    return _model


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

    response = _get_model().generate_content(prompt)
    digest = Digest(content=response.text.strip(), scope="philippines")
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
    response = _get_model().generate_content(GLOBAL_DIGEST_PROMPT.format(signals=signals_block))
    digest = Digest(content=response.text.strip(), scope="global")
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest
