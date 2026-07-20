"""GET /digest — latest daily digest. Phase 3."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import Digest

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("")
def get_latest_digest(db: Session = Depends(get_db)):
    latest = db.query(Digest).order_by(Digest.generated_at.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No digest generated yet")
    return {"content": latest.content, "generated_at": latest.generated_at}
