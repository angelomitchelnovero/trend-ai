"""GET /trending — current trending terms/topics. Phase 3."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import TrendingTerm

router = APIRouter(prefix="/trending", tags=["trending"])


@router.get("")
def get_trending(db: Session = Depends(get_db)):
    terms = (
        db.query(TrendingTerm)
        .order_by(TrendingTerm.captured_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "term": t.term,
            "source": t.source,
            "score": t.score,
            "captured_at": t.captured_at,
        }
        for t in terms
    ]
