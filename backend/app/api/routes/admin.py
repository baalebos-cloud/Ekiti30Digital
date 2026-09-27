"""Admin review of member-uploaded media assets.

Every route here requires a valid admin JWT (see app/core/auth.py). These are
the only routes allowed to query Asset without the approved-only filter in
app/services/assets.py.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import AdminUser, require_admin
from app.models.asset import Asset
from app.models.base import get_db
from app.schemas.assets import AssetOut, RejectRequest

router = APIRouter(
    prefix="/api/admin/assets",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _get_pending_asset(asset_id: int, db: Session) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if asset.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset has already been {asset.status}",
        )
    return asset


def _now() -> datetime:
    # Stored naive in UTC, matching the other DateTime columns.
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/pending", response_model=list[AssetOut])
def list_pending_assets(db: Session = Depends(get_db)):
    """All assets awaiting review, oldest first."""
    return (
        db.query(Asset)
        .filter(Asset.status == "pending")
        .order_by(Asset.created_at, Asset.id)
        .all()
    )


@router.post("/{asset_id}/approve", response_model=AssetOut)
def approve_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    asset = _get_pending_asset(asset_id, db)
    asset.status = "approved"
    asset.reviewed_by = admin.email
    asset.reviewed_at = _now()
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/{asset_id}/reject", response_model=AssetOut)
def reject_asset(
    asset_id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    asset = _get_pending_asset(asset_id, db)
    asset.status = "rejected"
    asset.rejection_reason = body.rejection_reason
    asset.reviewed_by = admin.email
    asset.reviewed_at = _now()
    db.commit()
    db.refresh(asset)
    return asset
