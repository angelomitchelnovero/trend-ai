"""
Live viewer count via a heartbeat pattern — not websockets, not a faked
number. The frontend pings /presence/heartbeat every ~20s with a random
per-tab session id (generated client-side, kept in memory for the tab's
lifetime); /presence/count counts distinct sessions seen in the last 45s.

Tradeoff worth being upfront about: this undercounts very briefly on a
closed tab (up to ~45s until it ages out), since there's no explicit
"I'm leaving" signal without websockets. That's a deliberate, honest
simplicity tradeoff — the alternative (websockets) is a bigger
infrastructure lift for a feature that's meant to be a nice-to-have
social-proof signal, not a precise analytics count.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schema import PresenceHeartbeat

router = APIRouter(prefix="/presence", tags=["presence"])

ACTIVE_WINDOW_SECONDS = 45


class HeartbeatRequest(BaseModel):
    session_id: str


@router.post("/heartbeat")
def heartbeat(body: HeartbeatRequest, db: Session = Depends(get_db)):
    existing = db.query(PresenceHeartbeat).filter_by(session_id=body.session_id).first()
    if existing:
        existing.last_seen = datetime.utcnow()
    else:
        db.add(PresenceHeartbeat(session_id=body.session_id, last_seen=datetime.utcnow()))
    db.commit()
    return {"ok": True}


@router.get("/count")
def count(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(seconds=ACTIVE_WINDOW_SECONDS)
    active = db.query(PresenceHeartbeat).filter(PresenceHeartbeat.last_seen >= cutoff).count()
    return {"count": active}
