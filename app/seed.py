"""
Seed the sources and categories tables. Run once after `alembic upgrade head`.

    python -m app.seed
"""

from app.database import SessionLocal
from app.models.schema import Category, Source

SOURCES = [
    {"name": "Rappler", "feed_url": "https://www.rappler.com/feed/"},
    {"name": "Inquirer", "feed_url": "https://newsinfo.inquirer.net/feed"},
    {"name": "GMA News", "feed_url": "https://data.gmanetwork.com/gno/rss/news/feed.xml"},
]

CATEGORIES = [
    "Politics",
    "Business",
    "Showbiz",
    "Sports",
    "Weather/Disaster",
    "Metro/Local",
]


def seed():
    db = SessionLocal()
    try:
        for s in SOURCES:
            if not db.query(Source).filter_by(name=s["name"]).first():
                db.add(Source(**s))

        for c in CATEGORIES:
            if not db.query(Category).filter_by(name=c).first():
                db.add(Category(name=c))

        db.commit()
        print(f"Seeded {len(SOURCES)} sources and {len(CATEGORIES)} categories.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
