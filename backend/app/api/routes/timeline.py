from fastapi import APIRouter

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("")
def list_timeline_events() -> dict:
    """Placeholder for the Ekiti Timeline feature.

    TODO: replace with real timeline events sourced from 03_Timeline/,
    backed by a SQLAlchemy model and Pydantic schema.
    """
    return {"message": "timeline endpoint not yet implemented", "events": []}
