"""The homepage's content in one response, edited through /api/admin/homepage/*."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.schemas.homepage import HomepageOut
from app.services import homepage

router = APIRouter(prefix="/api/homepage", tags=["homepage"])


@router.get("", response_model=HomepageOut)
def get_homepage(db: Session = Depends(get_db)):
    """The hero (null until set up) and the leaders, landmarks and moments, each in display order."""
    return homepage.public_homepage(db)
