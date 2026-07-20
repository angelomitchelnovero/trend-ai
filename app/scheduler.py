"""
APScheduler wiring — Phase 2 (raw ingestion polling) and Phase 4
(AI enrichment + scheduled digest). Run this as a background worker
process, separate from the FastAPI web process, on Fly.io/Railway.

    python -m app.scheduler
"""

from apscheduler.schedulers.blocking import BlockingScheduler

from app.ai.cluster import assign_clusters, embed_unprocessed
from app.ai.digest import generate_daily_digest
from app.ai.summarize import summarize_unprocessed
from app.database import SessionLocal
from app.ingestion.rss import ingest_all_sources
from app.ingestion.social_trends import (
    ingest_google_trends,
    ingest_reddit,
    reddit_configured,
    serpapi_configured,
)

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=20)
def poll_rss():
    db = SessionLocal()
    try:
        results = ingest_all_sources(db)
        print(f"[rss] {results}")
    finally:
        db.close()


@scheduler.scheduled_job("interval", minutes=30)
def poll_trends():
    db = SessionLocal()
    try:
        reddit_count = ingest_reddit(db)
        trends_count = ingest_google_trends(db)
        reddit_note = "" if reddit_configured() else " (not configured yet)"
        trends_note = "" if serpapi_configured() else " (not configured yet)"
        print(f"[trends] reddit={reddit_count}{reddit_note} google_trends={trends_count}{trends_note}")
    finally:
        db.close()


@scheduler.scheduled_job("interval", minutes=20)
def enrich_articles():
    db = SessionLocal()
    try:
        summarized = summarize_unprocessed(db)
        embedded = embed_unprocessed(db)
        clustered = assign_clusters(db)
        print(f"[enrich] summarized={summarized} embedded={embedded} clustered={clustered}")
    finally:
        db.close()


@scheduler.scheduled_job("cron", hour=6, minute=0)  # once daily, 6am
def build_daily_digest():
    db = SessionLocal()
    try:
        digest = generate_daily_digest(db)
        print(f"[digest] generated id={digest.id}")
    except ValueError as e:
        print(f"[digest] skipped: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()
