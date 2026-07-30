"""Five high-signal Philippine stories for the homepage's daily analyzer."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import Article

router = APIRouter(prefix="/news-analyzer", tags=["news analyzer"])

IMPACT_CATEGORIES = {"Politics": 6, "Finance": 6, "Weather/Disaster": 5, "AI": 4, "Tech": 4, "Local": 3}
IMPACT_TERMS = ("policy", "law", "economy", "inflation", "budget", "election", "court", "storm", "typhoon", "earthquake", "health", "transport")
LOW_SIGNAL_TERMS = (
    "arrest", "arrested", "nabbed", "human trafficking", "fake gold", "celebrity",
    "showbiz", "dating", "viral", "scandal", "gossip",
)


def _impact_score(article: Article) -> int:
    text = f"{article.title} {article.summary or article.raw_summary or ''}".lower()
    category = article.category.name if article.category else None
    score = IMPACT_CATEGORIES.get(category, 1)
    score += sum(term in text for term in IMPACT_TERMS)
    score += 2 if article.cluster_id else 0
    score -= 8 if any(term in text for term in LOW_SIGNAL_TERMS) else 0
    return score


@router.get("")
def get_daily_selection(db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=1)
    candidates = (
        db.query(Article).filter(Article.published_at >= since, Article.summary.isnot(None))
        .order_by(Article.published_at.desc()).limit(80).all()
    )
    selected, represented_clusters = [], set()
    for article in sorted(candidates, key=_impact_score, reverse=True):
        cluster_key = article.cluster_id or article.id
        if cluster_key in represented_clusters:
            continue
        represented_clusters.add(cluster_key)
        selected.append(article)
        if len(selected) == 5:
            break
    return {"items": [{
        "id": article.id, "title": article.title, "summary": article.summary,
        "url": article.url, "source": article.source.name if article.source else None,
        "category": article.category.name if article.category else None,
        "published_at": article.published_at, "impact_score": _impact_score(article),
    } for article in selected]}
