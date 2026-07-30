"""GET /trending — current trending terms/topics. Phase 3."""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import TrendingTerm

router = APIRouter(prefix="/trending", tags=["trending"])


@router.get("/timeline")
def global_timeline(days: int = 7, db: Session = Depends(get_db)):
    """Daily count of retained global AI and Tech signals for the dashboard timeline."""
    rows = (
        db.query(
            func.date(TrendingTerm.captured_at).label("day"),
            TrendingTerm.category_name.label("category"),
            func.count(TrendingTerm.id).label("count"),
        )
        .filter(TrendingTerm.scope == "global", TrendingTerm.category_name.in_(("AI", "Tech")))
        .group_by(func.date(TrendingTerm.captured_at), TrendingTerm.category_name)
        .order_by(func.date(TrendingTerm.captured_at).desc())
        .limit(min(days, 30) * 2)
        .all()
    )
    points: dict[str, dict[str, int | str]] = {}
    for row in rows:
        day = str(row.day)
        points.setdefault(day, {"day": day, "AI": 0, "Tech": 0})[row.category] = row.count
    return {"points": list(reversed(points.values()))}


@router.get("")
def get_trending(limit: int = 24, db: Session = Depends(get_db)):
    terms = (
        db.query(TrendingTerm)
        .order_by(
            case((TrendingTerm.category_name == "AI", 0), (TrendingTerm.category_name == "Tech", 1), else_=2),
            case((TrendingTerm.scope == "global", 0), else_=1),
            TrendingTerm.relevance_score.desc().nullslast(),
            TrendingTerm.score.desc().nullslast(),
            TrendingTerm.captured_at.desc(),
        )
        .limit(min(limit, 50))
        .all()
    )
    return [
        {
            "id": t.id,
            "term": t.term,
            "source": t.source,
            "score": t.score,
            "captured_at": t.captured_at,
            "title": t.title or t.term,
            "summary": t.summary,
            "url": t.url,
            "ticker": t.ticker,
            "category": t.category_name,
            "scope": t.scope,
        }
        for t in terms
    ]
