"""
RSS ingestion — promote this from experiments/01_rss_quality_check.py
once that experiment passes its exit criteria.

This is intentionally a thin stub: the parsing/cleanup logic should be
lifted from the experiment almost as-is, with the print statements
replaced by DB writes.
"""

import re
from datetime import datetime
from html import unescape

import feedparser
import requests
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from app.models.schema import Article, Source

HTML_TAG_RE = re.compile(r"<[^>]+>")
REQUEST_TIMEOUT = 15
USER_AGENT = "trendai-by-aloe/0.1"


def strip_html(text: str) -> str:
    return unescape(HTML_TAG_RE.sub("", text or "")).strip()


def fetch_and_store(source: Source, db: Session) -> int:
    """Fetch a source's RSS feed and upsert new articles. Returns count added."""
    resp = requests.get(source.feed_url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)

    added = 0
    for entry in parsed.entries:
        url = entry.get("link")
        if not url:
            continue

        exists = db.query(Article).filter_by(url=url).first()
        if exists:
            continue

        published_raw = entry.get("published")
        try:
            published_at = date_parser.parse(published_raw) if published_raw else datetime.utcnow()
        except (ValueError, TypeError):
            published_at = datetime.utcnow()

        article = Article(
            title=entry.get("title", "").strip(),
            raw_summary=strip_html(entry.get("summary", "")),
            url=url,
            published_at=published_at,
            source_id=source.id,
        )
        db.add(article)
        added += 1

    db.commit()
    return added


def ingest_all_sources(db: Session) -> dict:
    """Run fetch_and_store for every configured source. Returns per-source counts."""
    results = {}
    for source in db.query(Source).all():
        try:
            results[source.name] = fetch_and_store(source, db)
        except requests.RequestException as e:
            results[source.name] = f"failed: {e}"
    return results
