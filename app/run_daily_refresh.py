"""Run the complete low-cost daily refresh for the hosted Trend.ai instance.

Designed for a GitHub Actions schedule at 3:05 PM Asia/Manila (07:05 UTC).

Budget per run (free-tier limits):
- gemini-2.5-flash: 20 requests / day. Used for PH summaries + both digests.
- gemini-2.5-flash-lite: 20 requests / day. Used for global English briefs.
- Each AI step catches its own 429: a quota exhaustion in one step skips that
  step but lets the rest of the refresh finish, so we don't waste the day's
  budget on a late crash.
"""

import time

from google.api_core.exceptions import ResourceExhausted

from app.ai.digest import generate_daily_digest, generate_global_digest
from app.ai.summarize import SECONDS_BETWEEN_CALLS, summarize_unprocessed
from app.ai.trends import enrich_global_trends
from app.database import SessionLocal
from app.ingestion.gdelt import ingest_global_ai_tech
from app.ingestion.rss import ingest_all_sources
from app.ingestion.social_trends import ingest_google_trends, ingest_reddit

# Compact daily budget. Each limit fits well under one bucket's 20/day ceiling
# even after the rest of the day's prior runs (manual triggers, re-runs).
PH_SUMMARY_LIMIT = 4
GLOBAL_BRIEF_LIMIT = 4
DIGEST_STORY_LIMIT = 4


def _try(label, fn):
    """Run an AI step; convert a 429 into a clean 'skipped, retry tomorrow' log."""
    try:
        return ("ok", fn())
    except ResourceExhausted as exc:
        print(f"  {label} SKIPPED — quota exhausted. Will retry on next scheduled run. ({exc})")
        return ("skipped", None)
    except ValueError as exc:
        # Empty input — also benign, just no work to do today.
        print(f"  {label} skipped: {exc}")
        return ("skipped", None)


def main():
    db = SessionLocal()
    try:
        print("Refreshing Philippine news and local trends...")
        print(f"  RSS: {ingest_all_sources(db)}")
        print(f"  Google Trends: {ingest_google_trends(db)}")
        print(f"  Reddit: {ingest_reddit(db)}")

        # The pauses keep every Gemini request below the free-tier per-minute rate.
        status, n = _try(
            "Philippines summaries",
            lambda: summarize_unprocessed(db, limit=PH_SUMMARY_LIMIT),
        )
        print(f"  Philippines summaries: {n}")
        if status == "ok":
            time.sleep(SECONDS_BETWEEN_CALLS)
            status, _ = _try(
                "Philippines digest",
                lambda: generate_daily_digest(db, max_stories=DIGEST_STORY_LIMIT),
            )
            if status == "ok":
                print("  Philippines digest: ok")

        print(f"  Global AI/Tech signals: {ingest_global_ai_tech(db)}")
        time.sleep(SECONDS_BETWEEN_CALLS)
        status, n = _try(
            "Global English briefs",
            lambda: enrich_global_trends(db, limit=GLOBAL_BRIEF_LIMIT),
        )
        print(f"  Global English briefs: {n}")
        if status == "ok":
            time.sleep(SECONDS_BETWEEN_CALLS)
            status, _ = _try(
                "Global digest",
                lambda: generate_global_digest(db, max_signals=DIGEST_STORY_LIMIT),
            )
            if status == "ok":
                print("  Global digest: ok")
    finally:
        db.close()


if __name__ == "__main__":
    main()
