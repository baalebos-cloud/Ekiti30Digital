"""Media asset metadata for member uploads and admin approval.

The file itself lives in Cloudinary (uploaded directly from the browser via
an unsigned preset); this table only tracks metadata and review status.
Public-facing code must read assets through
app/services/assets.py:get_approved_assets_query, never directly.
"""

from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

ASSET_STATUSES = ("pending", "approved", "rejected")


class Asset(Base):
    """A member-contributed media asset awaiting or past admin review."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Filled in by POST /api/uploads/{id}/complete once the direct
    # Cloudinary upload has finished.
    public_id: Mapped[str | None]
    cloudinary_url: Mapped[str | None]

    # One of app/services/cloudinary_convention.py:ALLOWED_FOLDERS.
    folder: Mapped[str]

    contributor: Mapped[str]
    source: Mapped[str | None]
    location_lga: Mapped[str | None]
    description: Mapped[str | None] = mapped_column(Text)

    # e.g. "owned", "permission_granted", "public_domain". A plain string
    # rather than an enum until the allowed values are finalized.
    rights_status: Mapped[str]

    # Links to whatever project/content this asset belongs to.
    related_content_id: Mapped[str | None]

    # One of ASSET_STATUSES.
    status: Mapped[str] = mapped_column(
        default="pending", server_default="pending", index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
