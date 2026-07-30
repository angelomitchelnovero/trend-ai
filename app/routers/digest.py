"""GET /digest — latest daily digest. Phase 3."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import Digest
from app.ai.digest import generate_daily_digest, generate_global_digest

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("")
def get_latest_digest(db: Session = Depends(get_db)):
    latest = (db.query(Digest).filter(Digest.scope == "philippines")
              .order_by(Digest.generated_at.desc()).first())
    if not latest:
        try:
            latest = generate_daily_digest(db)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"content": latest.content, "generated_at": latest.generated_at}


@router.get("/global")
def get_latest_global_digest(db: Session = Depends(get_db)):
    latest = (db.query(Digest).filter(Digest.scope == "global")
              .order_by(Digest.generated_at.desc()).first())
    if not latest:
        try:
            latest = generate_global_digest(db)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"content": latest.content, "generated_at": latest.generated_at}
