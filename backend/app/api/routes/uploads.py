"""Member-facing media upload endpoints.

The file itself never passes through this backend: the browser uploads it
directly to Cloudinary using an unsigned preset. These endpoints only record
metadata before the upload (init) and the resulting Cloudinary identifiers
after it (complete). New assets start as "pending" and stay hidden from
public output until an admin approves them (see admin.py).

Both endpoints require a contributor or admin JWT (app/core/auth.py). Auth
is in addition to — not instead of — the folder check in init and the
Cloudinary verification in complete.
"""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import ContributorUser, require_contributor
from app.core.config import settings
from app.models.asset import Asset
from app.models.base import get_db
from app.schemas.assets import (
    AssetOut,
    UploadCompleteRequest,
    UploadInitRequest,
    UploadInitResponse,
)
from app.services import cloudinary_admin
from app.services.cloudinary_convention import (
    ALLOWED_FOLDERS,
    ALLOWED_FORMATS,
    MAX_UPLOAD_BYTES,
    validate_folder,
)

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Resource types our preset's ALLOWED_FORMATS can produce.
_RESOURCE_TYPES = ("image", "video")

# Conservative: the preset gives every upload a random public_id, so anything
# else (e.g. "..", "?", "#") is refused before it reaches an Admin API URL.
_PUBLIC_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+(/[A-Za-z0-9_\-]+)*$")


def _unprocessable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


def _cloudinary_config() -> tuple[str, str]:
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_UPLOAD_PRESET):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Media uploads are not configured",
        )
    return settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_UPLOAD_PRESET


@router.post("/init", response_model=UploadInitResponse, status_code=201)
def init_upload(
    body: UploadInitRequest,
    db: Session = Depends(get_db),
    user: ContributorUser = Depends(require_contributor),
):
    """Create a pending Asset and return what the browser needs to upload it.

    The uploader's identity is taken from the verified token, not the body.
    """
    cloud_name, upload_preset = _cloudinary_config()

    # Enforced for every caller, whatever their role.
    if not validate_folder(body.folder):
        raise _unprocessable(f"folder must be one of: {', '.join(ALLOWED_FOLDERS)}")

    asset = Asset(
        **body.model_dump(),
        contributor=user.display_name,
        created_by=user.owner_id,
        status="pending",
    )
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
    asset_id: int,
    body: UploadCompleteRequest,
    db: Session = Depends(get_db),
    user: ContributorUser = Depends(require_contributor),
):
    """Verify an upload with Cloudinary, then record its public_id and URL.

    Only the account that created the asset may complete it (403 otherwise,
    checked before anything about the asset's state is revealed).

    The browser supplies public_id and secure_url, so nothing is stored
    until the Cloudinary Admin API confirms the resource exists in our
    account, in the folder recorded at init, with an allowed format and
    size. On any failure the Asset is left untouched.
    """
    cloud_name, _ = _cloudinary_config()

    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    # Ownership comes first so a non-owner learns nothing about the asset's
    # state. Strict for every role: admins review assets via /api/admin, they
    # do not complete other people's uploads. Rows with no owner (created
    # before this check existed) match nobody.
    if asset.created_by is None or asset.created_by != user.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own uploads",
        )
    if asset.status != "pending" or asset.public_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Upload for this asset has already been completed",
        )

    # Cheap sanity checks on the client's values before calling Cloudinary.
    url_prefix = f"https://res.cloudinary.com/{cloud_name}/"
    if not body.secure_url.startswith(url_prefix):
        raise _unprocessable("secure_url is not a Cloudinary URL for this account")
    if body.public_id not in body.secure_url:
        raise _unprocessable("public_id does not match secure_url")
    if not _PUBLIC_ID_RE.fullmatch(body.public_id):
        raise _unprocessable("public_id is not valid")
    resource_type = body.secure_url[len(url_prefix):].split("/", 1)[0]
    if resource_type not in _RESOURCE_TYPES:
        raise _unprocessable("secure_url is not an image or video upload")

    # Authoritative check against Cloudinary itself.
    try:
        resource = cloudinary_admin.get_resource(body.public_id, resource_type)
    except cloudinary_admin.CloudinaryNotConfigured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Upload verification is not configured",
        ) from None
    except cloudinary_admin.CloudinaryLookupError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not verify the upload with Cloudinary",
        ) from None

    if resource is None:
        raise _unprocessable("No such upload exists in Cloudinary")
    if resource.get("public_id") != body.public_id:
        raise _unprocessable("Cloudinary resource does not match public_id")
    if cloudinary_admin.resource_folder(resource) != asset.folder:
        raise _unprocessable("Upload is not in the folder this asset was created for")
    # Defense in depth: the preset already enforces formats and the
    # frontend the size limit.
    if resource.get("format") not in ALLOWED_FORMATS:
        raise _unprocessable("Upload format is not allowed")
    if not isinstance(resource.get("bytes"), int) or resource["bytes"] > MAX_UPLOAD_BYTES:
        raise _unprocessable("Upload exceeds the maximum file size")

    asset.public_id = resource["public_id"]
    # Cloudinary's own URL rather than the one the browser sent.
    asset.cloudinary_url = resource.get("secure_url") or body.secure_url
    db.commit()
    db.refresh(asset)
    return asset
