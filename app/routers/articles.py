"""GET /articles — paginated, filterable by category/source/date. Phase 3."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import Article

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(
    category: Optional[str] = None,
    source: Optional[str] = None,
    since: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Article)

    if category:
        query = query.join(Article.category).filter_by(name=category)
    if source:
        query = query.join(Article.source).filter_by(name=source)
    if since:
        query = query.filter(Article.published_at >= since)

    total = query.count()
    items = (
        query.order_by(Article.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary,
                "url": a.url,
                "published_at": a.published_at,
                "source": a.source.name if a.source else None,
                "category": a.category.name if a.category else None,
                "cluster_id": a.cluster_id,
            }
            for a in items
        ],
    }
