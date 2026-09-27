"""Member-facing media upload endpoints.

The file itself never passes through this backend: the browser uploads it
directly to Cloudinary using an unsigned preset. These endpoints only record
metadata before the upload (init) and the resulting Cloudinary identifiers
after it (complete). New assets start as "pending" and stay hidden from
public output until an admin approves them (see admin.py).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asset import Asset
from app.models.base import get_db
from app.schemas.assets import (
    AssetOut,
    UploadCompleteRequest,
    UploadInitRequest,
    UploadInitResponse,
)
from app.services.cloudinary_convention import (
    ALLOWED_FOLDERS,
    ALLOWED_FORMATS,
    MAX_UPLOAD_BYTES,
    validate_folder,
)

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


def _cloudinary_config() -> tuple[str, str]:
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_UPLOAD_PRESET):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Media uploads are not configured",
        )
    return settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_UPLOAD_PRESET


@router.post("/init", response_model=UploadInitResponse, status_code=201)
def init_upload(body: UploadInitRequest, db: Session = Depends(get_db)):
    """Create a pending Asset and return what the browser needs to upload it."""
    cloud_name, upload_preset = _cloudinary_config()

    if not validate_folder(body.folder):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"folder must be one of: {', '.join(ALLOWED_FOLDERS)}",
        )

    asset = Asset(**body.model_dump(), status="pending")
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return UploadInitResponse(
        asset_id=asset.id,
        cloud_name=cloud_name,
        upload_preset=upload_preset,
        folder=asset.folder,
        max_file_bytes=MAX_UPLOAD_BYTES,
        allowed_formats=list(ALLOWED_FORMATS),
    )


@router.post("/{asset_id}/complete", response_model=AssetOut)
def complete_upload(
    asset_id: int, body: UploadCompleteRequest, db: Session = Depends(get_db)
):
    """Record the public_id and secure_url Cloudinary returned for an upload."""
    cloud_name, _ = _cloudinary_config()

    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if asset.status != "pending" or asset.public_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Upload for this asset has already been completed",
        )

    # The browser supplies these values, so at least make sure they point
    # at our own Cloudinary account. This can't prove the file exists —
    # that would need the Admin API (and so the API secret) server-side.
    if not body.secure_url.startswith(f"https://res.cloudinary.com/{cloud_name}/"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="secure_url is not a Cloudinary URL for this account",
        )
    if body.public_id not in body.secure_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="public_id does not match secure_url",
        )

    asset.public_id = body.public_id
    asset.cloudinary_url = body.secure_url
    db.commit()
    db.refresh(asset)
    return asset
