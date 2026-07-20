"""Database engine/session setup. Phase 1."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Loads variables from a .env file in the project root, if present.
# Explicit environment variables (e.g. set in your shell) still take
# priority and are never overridden by this.
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/trendai")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
