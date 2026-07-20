"""
Daily digest generation — promote this from
experiments/05_digest_check.py once that experiment's output is judged
good enough to show on the dashboard.
"""

import os
from datetime import datetime, timedelta

import google.generativeai as genai
from sqlalchemy.orm import Session

from app.models.schema import Article, Digest

DIGEST_PROMPT = """You are writing a short daily "what's trending in the
Philippines" briefing for a news dashboard. Below are today's top story
headlines and summaries from multiple outlets. Write a single cohesive
briefing (150-250 words) that groups related stories, highlights what
matters most, and reads naturally rather than as a bullet dump. Keep a
neutral, informative tone — this is a news digest, not opinion content.

Stories:
{stories}

Daily briefing:"""

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
    digest = Digest(content=response.text.strip())
    db.add(digest)
    db.commit()
    db.refresh(digest)
    return digest
