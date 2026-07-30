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

from app.categorize import classify
from app.models.schema import Article, Category, Source

HTML_TAG_RE = re.compile(r"<[^>]+>")
REQUEST_TIMEOUT = 15
USER_AGENT = "trendai-by-aloe/0.1"


def strip_html(text: str) -> str:
    return unescape(HTML_TAG_RE.sub("", text or "")).strip()


_category_cache: dict[str, int] = {}


def _get_category_id(db: Session, name: str | None) -> int | None:
    """Looks up (or creates) the Category row for a classifier result.
    Cached per-process since the category set is small and fixed."""
    if not name:
        return None
    if name in _category_cache:
        return _category_cache[name]

    category = db.query(Category).filter_by(name=name).first()
    if not category:
        category = Category(name=name)
        db.add(category)
        db.flush()  # get category.id without a full commit

    _category_cache[name] = category.id
    return category.id


def fetch_and_store(source: Source, db: Session, verbose: bool = False) -> int:
    """Fetch a source's RSS feed and upsert new articles. Returns count added.

    Pass verbose=True to print diagnostics — useful when a source returns 0
    and it's unclear whether that's "nothing new" or something failing
    silently (blocked request, empty/broken feed, all entries missing a
    link, etc).
    """
    resp = requests.get(source.feed_url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)

    if verbose:
        print(f"    [{source.name}] HTTP {resp.status_code}, {len(resp.content)} bytes, "
              f"{len(parsed.entries)} entries in feed, bozo={parsed.bozo}"
              + (f" ({parsed.bozo_exception})" if parsed.bozo else ""))

    added = 0
    skipped_no_link = 0
    skipped_duplicate = 0

    for entry in parsed.entries:
        url = entry.get("link")
        if not url:
            skipped_no_link += 1
            continue

        exists = db.query(Article).filter_by(url=url).first()
        if exists:
            skipped_duplicate += 1
            continue

        published_raw = entry.get("published")
        try:
            published_at = date_parser.parse(published_raw) if published_raw else datetime.utcnow()
        except (ValueError, TypeError):
            published_at = datetime.utcnow()

        title = entry.get("title", "").strip()
        raw_summary = strip_html(entry.get("summary", ""))

        article = Article(
            title=title,
            raw_summary=raw_summary,
            url=url,
            published_at=published_at,
            source_id=source.id,
            category_id=_get_category_id(db, classify(f"{title} {raw_summary}")),
        )
        db.add(article)
        added += 1

    db.commit()

    if verbose:
        print(f"    [{source.name}] added={added} skipped_duplicate={skipped_duplicate} "
              f"skipped_no_link={skipped_no_link}")

    return added


def ingest_all_sources(db: Session, verbose: bool = False) -> dict:
    """Run fetch_and_store for every configured source. Returns per-source counts."""
    results = {}
    for source in db.query(Source).all():
        try:
            results[source.name] = fetch_and_store(source, db, verbose=verbose)
        except requests.RequestException as e:
            results[source.name] = f"failed: {e}"
    return results
