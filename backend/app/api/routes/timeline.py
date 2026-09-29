"""Ekiti Timeline: events loaded by scripts/ingest_timeline.py."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.timeline_event import TimelineEvent
from app.schemas.timeline import TimelineEventOut, TimelineListResponse

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("", response_model=TimelineListResponse)
def list_timeline_events(db: Session = Depends(get_db)):
    """Every event, oldest first, whatever its verification status.

    date_start is ISO text at the event's own precision, so it sorts by date
    as a plain string; id breaks ties so the order is stable. Sorted here
    rather than in SQL, where Postgres's locale collation may ignore the
    hyphens.
    """
    events = sorted(db.query(TimelineEvent).all(), key=lambda e: (e.date_start, e.id))
    return TimelineListResponse(events=[TimelineEventOut.from_model(e) for e in events])
