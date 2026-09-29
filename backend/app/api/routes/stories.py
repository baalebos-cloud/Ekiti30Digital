from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.asset import Asset
from app.core.auth import ContributorUser, require_contributor
from app.schemas.assets import UploadInitRequest, AssetOut
from app.services.assets import get_approved_assets_query

router = APIRouter(prefix="/api/stories", tags=["Stories"])

@router.post("/", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_community_story(
    story_in: UploadInitRequest,
    db: Session = Depends(get_db),
    user: ContributorUser = Depends(require_contributor)
):
    """
    Submit a new 'My Story' entry for community archiving and admin review.
    Enforces authenticated contributor access and verified identity ownership.
    
    Note: Reuses UploadInitRequest schema to treat My Story submissions as 
    standard Asset records pending review.
    """
    db_asset = Asset(
        folder=story_in.folder if story_in.folder else "EKITI30/Stories",
        source=story_in.source,
        location_lga=story_in.location_lga,
        description=story_in.description,
        rights_status=story_in.rights_status,
        related_content_id=story_in.related_content_id,
        status="pending",
        contributor=user.display_name,
        created_by=user.owner_id,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.get("/", response_model=list[AssetOut])
def list_community_stories(
    db: Session = Depends(get_db)
):
    """
    List approved community stories for public viewing or frontend integration.
    Enforces moderation compliance by using get_approved_assets_query and 
    exact folder filtering for 'EKITI30/Stories'.
    """
    stmt = (
        get_approved_assets_query(db)
        .filter(Asset.folder == "EKITI30/Stories")
        .order_by(Asset.created_at.desc())
    )
    return stmt.all()
