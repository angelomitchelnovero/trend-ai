"""Discover global AI and technology stories through GDELT's public DOC API."""

from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.categorize import classify
from app.models.schema import TrendingTerm

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
REQUEST_TIMEOUT = 20
QUERIES = {
    "AI": '("artificial intelligence" OR OpenAI OR Anthropic OR Gemini OR ChatGPT OR "AI model")',
    "Tech": '(technology OR semiconductor OR cybersecurity OR robotics OR "data center")',
}
TICKERS = {
    "nvidia": "$NVDA", "microsoft": "$MSFT", "alphabet": "$GOOGL", "google": "$GOOGL",
    "meta": "$META", "apple": "$AAPL", "amd": "$AMD", "tesla": "$TSLA",
}


def _ticker(text: str) -> str | None:
    lowered = text.lower()
    return next((ticker for name, ticker in TICKERS.items() if name in lowered), None)


def ingest_global_ai_tech(db: Session, max_per_category: int = 8) -> int:
    """Store fresh, de-duplicated global AI/Tech card metadata from GDELT."""
    added = 0
    for requested_category, query in QUERIES.items():
        try:
            response = requests.get(
                GDELT_DOC_API,
                params={
                    "query": query, "mode": "ArtList", "format": "json",
                    "maxrecords": max_per_category, "timespan": "24h", "sort": "HybridRel",
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            stories = response.json().get("articles", [])
        except (requests.RequestException, ValueError) as exc:
            print(f"  GDELT {requested_category} fetch failed ({exc}) - skipping.")
            continue

        for rank, story in enumerate(stories, 1):
            title = (story.get("title") or "").strip()
            url = story.get("url")
            if not title or not url or db.query(TrendingTerm).filter_by(source="gdelt", url=url).first():
                continue
            db.add(TrendingTerm(
                term=title, title=title, url=url, source="gdelt", scope="global",
                score=max_per_category - rank + 1, relevance_score=100 - rank,
                # Query intent wins here: an AI release mentioning a chipmaker
                # is still an AI trend, not a generic Tech trend.
                category_name=requested_category, ticker=_ticker(title),
                captured_at=datetime.utcnow(),
            ))
            added += 1
        db.commit()
    return added
