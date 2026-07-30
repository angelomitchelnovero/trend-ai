"""Fetch global AI and Tech cards immediately, without waiting for the scheduler.

    python -m app.run_global_trends_once
"""

from app.database import SessionLocal
from app.ingestion.gdelt import ingest_global_ai_tech
from app.ai.trends import enrich_global_trends
from app.ai.digest import generate_global_digest


def main():
    db = SessionLocal()
    try:
        count = ingest_global_ai_tech(db)
        enriched = enrich_global_trends(db, limit=8)
        try:
            digest = generate_global_digest(db)
            digest_note = f", global digest #{digest.id} generated"
        except ValueError:
            digest_note = ""
        print(f"Added {count} global card(s), enriched {enriched}{digest_note}. Refresh localhost:3000 to view them.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
