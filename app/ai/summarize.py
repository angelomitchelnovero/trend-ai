"""
Summarization — promote this from experiments/02_summarization_check.py
once that experiment's output quality is judged good enough.
"""

import os
import time

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from sqlalchemy.orm import Session

from app.models.schema import Article

SUMMARY_PROMPT = """You are summarizing a Philippine news article for a daily
trending briefing. Write a concise 2-3 sentence summary in English, but keep
any Taglish terms, local place names, or local context in the original
article intact rather than translating them away. Be accurate — do not add
facts that aren't in the source text.

Title: {title}

Article text:
{body}

Summary:"""

# Free-tier Gemini quota for gemini-2.5-flash is 5 requests/minute. Pausing
# this long between calls keeps us comfortably under that instead of
# hitting 429s. If you're on a paid tier, feel free to shrink this.
SECONDS_BETWEEN_CALLS = 13
MAX_RETRIES_ON_RATE_LIMIT = 3
RATE_LIMIT_RETRY_WAIT = 20

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


def summarize_article(article: Article) -> str:
    prompt = SUMMARY_PROMPT.format(title=article.title, body=article.raw_summary or "")

    for attempt in range(1, MAX_RETRIES_ON_RATE_LIMIT + 1):
        try:
            response = _get_model().generate_content(prompt)
            return response.text.strip()
        except ResourceExhausted:
            if attempt == MAX_RETRIES_ON_RATE_LIMIT:
                raise
            print(f"    Rate limited — waiting {RATE_LIMIT_RETRY_WAIT}s (retry {attempt}/{MAX_RETRIES_ON_RATE_LIMIT})...")
            time.sleep(RATE_LIMIT_RETRY_WAIT)

    raise RuntimeError("unreachable")  # loop always returns or raises above


def summarize_unprocessed(db: Session, limit: int = 20) -> int:
    """Summarize articles that don't have an AI summary yet. Prioritizes the
    newest articles first — otherwise, with a backlog of older unsummarized
    articles, this would keep chipping away at old news and the daily
    digest's 24h window would never find anything fresh to work with.
    Paced to stay under the free-tier rate limit, and commits after each
    article so progress isn't lost if a later one fails."""
    articles = (
        db.query(Article)
        .filter(Article.summary.is_(None))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )
    count = 0
    for i, article in enumerate(articles):
        if not article.raw_summary:
            continue

        print(f"  [{i + 1}/{len(articles)}] Summarizing: {article.title[:60]}...")
        article.summary = summarize_article(article)
        db.commit()
        count += 1

        if i < len(articles) - 1:
            time.sleep(SECONDS_BETWEEN_CALLS)

    return count
