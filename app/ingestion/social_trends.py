"""
Reddit + Google Trends ingestion — promoted from
experiments/04_trending_signal_check.py.

Both sources are OPTIONAL and fail gracefully (return 0, log why) rather
than crashing ingestion:

- Reddit: no-op until REDDIT_CLIENT_ID/SECRET are set, since new Reddit
  API access requires manual approval under their Responsible Builder
  Policy (see experiments/04_trending_signal_check.py for the request-
  form link).

- Google Trends: uses SerpApi's Trending Now endpoint instead of the
  `pytrends` library. pytrends scraped an unofficial Google endpoint and
  its GitHub repo was archived by its own maintainers in April 2025 —
  it's permanently unmaintained and its calls now 404. SerpApi is a paid
  service with a free tier (100 searches/month at serpapi.com) that
  returns structured, official-source-adjacent JSON instead of scraping.
  No-op until SERPAPI_KEY is set.
"""

import os

import requests
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.categorize import classify
from app.models.schema import TrendingTerm

SUBREDDIT = "Philippines"
NUM_POSTS = 15

SERPAPI_TRENDING_URL = "https://serpapi.com/search.json"
SERPAPI_GEO = "PH"
REQUEST_TIMEOUT = 15

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False


def reddit_configured() -> bool:
    return bool(os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET"))


def serpapi_configured() -> bool:
    return bool(os.environ.get("SERPAPI_KEY"))


def _reddit_client():
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ.get("REDDIT_USER_AGENT", "trendai-by-aloe/0.1"),
    )


def _previous_score(db: Session, term: str, source: str) -> int | None:
    """Looks up this same term's most recent prior score, for velocity
    tracking. Not yet surfaced in the UI — see TrendingTerm.previous_score
    docstring in app/models/schema.py."""
    prior = (
        db.query(TrendingTerm)
        .filter(TrendingTerm.term == term, TrendingTerm.source == source)
        .order_by(desc(TrendingTerm.captured_at))
        .first()
    )
    return prior.score if prior else None


def ingest_reddit(db: Session) -> int:
    """Returns count of trending terms added. Returns 0 (no-op) if Reddit
    isn't installed/configured yet — this is expected while waiting on
    Reddit's API approval, not an error."""
    if not REDDIT_AVAILABLE or not reddit_configured():
        return 0

    reddit = _reddit_client()
    added = 0
    for submission in reddit.subreddit(SUBREDDIT).hot(limit=NUM_POSTS):
        if submission.stickied:
            continue
        db.add(TrendingTerm(
            term=submission.title,
            source="reddit",
            scope="philippines",
            score=submission.score,
            category_name=classify(submission.title),
            previous_score=_previous_score(db, submission.title, "reddit"),
        ))
        added += 1
    db.commit()
    return added


def ingest_google_trends(db: Session) -> int:
    """Returns count of trending terms added. Returns 0 (no-op) if
    SERPAPI_KEY isn't set, or logs and returns 0 if the request fails."""
    if not serpapi_configured():
        return 0

    try:
        resp = requests.get(
            SERPAPI_TRENDING_URL,
            params={
                "engine": "google_trends_trending_now",
                "geo": SERPAPI_GEO,
                "api_key": os.environ["SERPAPI_KEY"],
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"  SerpApi Google Trends fetch failed ({e}) — skipping.")
        return 0

    trending = data.get("trending_searches", [])
    added = 0
    for rank, item in enumerate(trending, 1):
        term = item.get("query")
        if not term:
            continue
        score = item.get("search_volume", rank)
        db.add(TrendingTerm(
            term=term,
            source="google_trends",
            scope="philippines",
            score=score,
            category_name=classify(term),
            previous_score=_previous_score(db, term, "google_trends"),
        ))
        added += 1
    db.commit()
    return added
