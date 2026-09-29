"""Explore Ekiti: the 16 LGAs, loaded by scripts/ingest_lgas.py."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.lga import Lga
from app.schemas.lgas import LgaListResponse, LgaOut

router = APIRouter(prefix="/api/lgas", tags=["lgas"])


@router.get("", response_model=LgaListResponse)
def list_lgas(db: Session = Depends(get_db)):
    """Every LGA, alphabetically, with its verification_status as the source has it."""
    lgas = db.query(Lga).order_by(Lga.slug).all()
    return LgaListResponse(lgas=[LgaOut.from_model(lga) for lga in lgas])
