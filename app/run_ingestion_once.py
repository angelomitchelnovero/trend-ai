"""
Run ingestion once, immediately — for local testing, so you don't have
to wait on the scheduler's polling interval to see real data.

    python -m app.run_ingestion_once
"""

from app.database import SessionLocal
from app.ingestion.rss import ingest_all_sources
from app.ingestion.social_trends import ingest_google_trends, ingest_reddit, reddit_configured


def main():
    db = SessionLocal()
    try:
        print("Ingesting RSS feeds...")
        rss_results = ingest_all_sources(db, verbose=True)
        for source, result in rss_results.items():
            print(f"  {source}: {result}")

        print("\nIngesting Google Trends...")
        trends_count = ingest_google_trends(db)
        print(f"  google_trends: {trends_count} terms added")

        print("\nIngesting Reddit...")
        if reddit_configured():
            reddit_count = ingest_reddit(db)
            print(f"  reddit: {reddit_count} terms added")
        else:
            print("  reddit: skipped (not configured — see earlier note on API approval)")

        print("\nDone. Refresh localhost:3000 to see real data.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
