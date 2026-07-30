"""
SQLAlchemy models — Phase 1 schema.

Tables per README: articles, sources, categories, trending_terms, clusters.
Requires the pgvector extension for the embedding column
(`CREATE EXTENSION IF NOT EXISTS vector;` — see README deployment steps).
"""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base

# Gemini text-embedding-004 produces 768-dim vectors.
EMBEDDING_DIM = 768


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)       # e.g. "Rappler"
    feed_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    articles = relationship("Article", back_populates="source")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)        # Politics, Business, Showbiz, ...

    articles = relationship("Article", back_populates="category")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True)
    representative_title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    articles = relationship("Article", back_populates="cluster")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    summary = Column(Text)                # AI-generated summary
    raw_summary = Column(Text)            # original RSS summary, pre-cleanup
    url = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    source_id = Column(Integer, ForeignKey("sources.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)

    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)

    source = relationship("Source", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    cluster = relationship("Cluster", back_populates="articles")


class TrendingTerm(Base):
    __tablename__ = "trending_terms"

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False)
    source = Column(String, nullable=False)   # "reddit" | "google_trends"
    score = Column(Integer, nullable=True)     # e.g. reddit score, trends rank/volume
    captured_at = Column(DateTime, default=datetime.utcnow)

    # Shared category system: reuses the same category names as Article
    # (Politics, Business, Showbiz, Sports, Weather/Disaster, Metro/Local),
    # assigned via lightweight keyword matching at ingestion time — see
    # app/categorize.py. Stored as a plain string rather than a FK since
    # every capture is a new row (trending snapshots aren't updated in
    # place), and a string keeps ingestion simple/fast (no lookup needed).
    category_name = Column(String, nullable=True)

    # Velocity groundwork: the score this same term had on its previous
    # capture, if any. Lets a future feature compute "climbing fast" vs
    # "steady" without needing a full time-series query. Not yet surfaced
    # in the UI — see app/ingestion/social_trends.py for how it's set.
    previous_score = Column(Integer, nullable=True)

    # Optional enriched card fields. Legacy Google/Reddit snapshots keep
    # working because the API falls back to ``term`` when they are absent.
    scope = Column(String, nullable=False, default="philippines")
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    ticker = Column(String, nullable=True)
    relevance_score = Column(Integer, nullable=True)


class Digest(Base):
    """Not in the README's original table list, but needed to serve
    GET /digest without regenerating it on every request. Add via a new
    Alembic migration alongside the rest of the Phase 1 schema."""

    __tablename__ = "digests"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    scope = Column(String, nullable=False, default="philippines")
    generated_at = Column(DateTime, default=datetime.utcnow)


class PresenceHeartbeat(Base):
    """Backs the live viewer count. The frontend pings /presence/heartbeat
    every ~20s with a random per-tab session id; /presence/count counts
    distinct session ids seen in the last ~45s. This is a real count, not
    a faked/inflated number — it just undercounts slightly by design
    (anyone who closes the tab without a final ping ages out naturally
    rather than needing an explicit disconnect signal, which would need
    websockets)."""

    __tablename__ = "presence_heartbeats"

    session_id = Column(String, primary_key=True)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
