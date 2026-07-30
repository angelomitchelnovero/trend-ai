"""Run the complete low-cost daily refresh for the hosted Trend.ai instance.

Designed for a GitHub Actions schedule at 3:05 PM Asia/Manila (07:05 UTC).
"""

from app.ai.digest import generate_daily_digest, generate_global_digest
import time

from app.ai.summarize import SECONDS_BETWEEN_CALLS, summarize_unprocessed
from app.ai.trends import enrich_global_trends
from app.database import SessionLocal
from app.ingestion.gdelt import ingest_global_ai_tech
from app.ingestion.rss import ingest_all_sources
from app.ingestion.social_trends import ingest_google_trends, ingest_reddit


def main():
    db = SessionLocal()
    try:
        print("Refreshing Philippine news and local trends...")
        print(f"  RSS: {ingest_all_sources(db)}")
        print(f"  Google Trends: {ingest_google_trends(db)}")
        print(f"  Reddit: {ingest_reddit(db)}")

        # The pauses keep every Gemini request below the free-tier per-minute rate.
        print(f"  Philippines summaries: {summarize_unprocessed(db, limit=4)}")
        time.sleep(SECONDS_BETWEEN_CALLS)
        try:
            print(f"  Philippines digest: #{generate_daily_digest(db, max_stories=4).id}")
        except ValueError as exc:
            print(f"  Philippines digest skipped: {exc}")

        print(f"  Global AI/Tech signals: {ingest_global_ai_tech(db)}")
        time.sleep(SECONDS_BETWEEN_CALLS)
        print(f"  Global English briefs: {enrich_global_trends(db, limit=4)}")
        time.sleep(SECONDS_BETWEEN_CALLS)
        try:
            print(f"  Global digest: #{generate_global_digest(db, max_signals=4).id}")
        except ValueError as exc:
            print(f"  Global digest skipped: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
