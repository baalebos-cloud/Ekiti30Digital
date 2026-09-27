from fastapi import APIRouter

router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.get("")
def list_stories() -> dict:
    """Placeholder for the My Ekiti Story feature.

    TODO: replace with real citizen story submissions/listing, backed by
    a SQLAlchemy model and Pydantic schema.
    """
    return {"message": "stories endpoint not yet implemented", "stories": []}
