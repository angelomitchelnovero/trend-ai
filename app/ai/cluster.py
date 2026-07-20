"""
Embedding-based clustering — promote this from
experiments/03_clustering_check.py once that experiment shows a clean
separation between same-event and unrelated-story similarity scores.
"""

import os

import google.generativeai as genai
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.schema import Article, Cluster

EMBEDDING_MODEL = "models/text-embedding-004"

# Tune this based on the gap observed in Experiment 3 — start with the
# midpoint between the same-event and control averages, not a guess.
SIMILARITY_THRESHOLD = 0.85

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _configured = True


def embed_article(article: Article) -> list[float]:
    _ensure_configured()
    text = f"{article.title} {article.summary or article.raw_summary or ''}"
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return result["embedding"]


def embed_unprocessed(db: Session, limit: int = 20) -> int:
    articles = db.query(Article).filter(Article.embedding.is_(None)).limit(limit).all()
    count = 0
    for article in articles:
        article.embedding = embed_article(article)
        count += 1
    db.commit()
    return count


def assign_clusters(db: Session, limit: int = 20) -> int:
    """Naive nearest-neighbor clustering: attach each unclustered article
    to the closest existing cluster if within threshold, else start a new
    cluster. Good enough for v1 — revisit if cluster quality is poor."""
    unclustered = (
        db.query(Article)
        .filter(Article.cluster_id.is_(None), Article.embedding.isnot(None))
        .limit(limit)
        .all()
    )

    count = 0
    for article in unclustered:
        nearest = (
            db.query(Article)
            .filter(Article.cluster_id.isnot(None))
            .order_by(Article.embedding.cosine_distance(article.embedding))
            .first()
        )

        if nearest:
            distance = db.scalar(
                func.cosine_distance(nearest.embedding, article.embedding)
            )
            similarity = 1 - distance if distance is not None else 0
        else:
            similarity = 0

        if nearest and similarity >= SIMILARITY_THRESHOLD:
            article.cluster_id = nearest.cluster_id
        else:
            new_cluster = Cluster(representative_title=article.title)
            db.add(new_cluster)
            db.flush()  # get new_cluster.id
            article.cluster_id = new_cluster.id

        count += 1

    db.commit()
    return count
