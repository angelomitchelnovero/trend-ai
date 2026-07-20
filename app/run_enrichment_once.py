"""
Run AI enrichment once, immediately — summarization + digest generation —
for local testing, so you don't have to wait on the scheduler's daily
digest cron job to see the AI half working.

Free-tier Gemini quota is 5 requests/minute, so this paces itself
(~13s between calls) rather than blowing through the limit. Default
batch size (8) matches the digest's max_stories, so one run is enough
to populate both the ticker cards and the digest banner.

    python -m app.run_enrichment_once
"""

from app.ai.digest import generate_daily_digest
from app.ai.summarize import SECONDS_BETWEEN_CALLS, summarize_unprocessed
from app.database import SessionLocal

BATCH_SIZE = 8


def main():
    db = SessionLocal()
    try:
        est_seconds = BATCH_SIZE * SECONDS_BETWEEN_CALLS
        print(f"Summarizing up to {BATCH_SIZE} unprocessed articles "
              f"(~{est_seconds}s, paced to stay under the free-tier rate limit)...")
        summarized = summarize_unprocessed(db, limit=BATCH_SIZE)
        print(f"  {summarized} article(s) summarized")

        if summarized == 0:
            print("  Nothing to summarize — either all articles already have")
            print("  summaries, or run app.run_ingestion_once first to get articles.")

        print("\nGenerating daily digest...")
        try:
            digest = generate_daily_digest(db)
            print(f"  Digest #{digest.id} generated ({len(digest.content)} chars)")
        except ValueError as e:
            print(f"  Skipped: {e}")

        print("\nDone. Refresh localhost:3000 to see summaries + digest.")
        print(f"(Run again to summarize the next {BATCH_SIZE} — it always picks up where it left off.)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
