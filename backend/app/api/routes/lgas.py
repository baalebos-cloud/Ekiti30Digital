from fastapi import APIRouter

router = APIRouter(prefix="/api/lgas", tags=["lgas"])


@router.get("")
def list_lgas() -> dict:
    """Placeholder for the Explore Ekiti (LGAs) feature.

    TODO: replace with real data for all 16 LGAs sourced from 02_LGAs/,
    backed by a SQLAlchemy model and Pydantic schema.
    """
    return {"message": "lgas endpoint not yet implemented", "lgas": []}
