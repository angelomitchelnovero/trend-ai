"""
GET /search — keyword search across both signals (articles + trending
terms), with an optional category filter.

Keyword matching only for now (SQL ILIKE), not semantic/embedding search.
Semantic search needs precomputed article embeddings (see app/ai/cluster.py)
run at scale first — worth adding once that's validated, not before.

A search returning trending terms but zero matching articles is itself a
useful signal ("trending but unreported") — deliberately not special-cased
here, it just falls out of the response naturally: check
`trending_terms non-empty and articles empty` client-side.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import Article, TrendingTerm

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(
    q: str | None = Query(None, min_length=1),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    if not q and not category:
        raise HTTPException(status_code=400, detail="Provide at least one of q or category")

    articles_query = db.query(Article)
    if q:
        like_pattern = f"%{q}%"
        articles_query = articles_query.filter(
            or_(Article.title.ilike(like_pattern), Article.summary.ilike(like_pattern))
        )
    if category:
        articles_query = articles_query.join(Article.category).filter_by(name=category)
    articles = articles_query.order_by(Article.published_at.desc()).limit(30).all()

    terms_query = db.query(TrendingTerm)
    if q:
        terms_query = terms_query.filter(TrendingTerm.term.ilike(f"%{q}%"))
    if category:
        terms_query = terms_query.filter(TrendingTerm.category_name == category)
    terms = terms_query.order_by(TrendingTerm.captured_at.desc()).limit(20).all()

    return {
        "query": q or "",
        "category": category,
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary,
                "url": a.url,
                "published_at": a.published_at,
                "source": a.source.name if a.source else None,
                "category": a.category.name if a.category else None,
            }
            for a in articles
        ],
        "trending_terms": [
            {
                "term": t.term,
                "source": t.source,
                "score": t.score,
                "category": t.category_name,
            }
            for t in terms
        ],
        # True when trending terms matched but no articles did — the
        # "trending but unreported" signal, computed here rather than
        # stored, since it's just a property of this specific search.
        "trending_but_unreported": len(terms) > 0 and len(articles) == 0,
    }
