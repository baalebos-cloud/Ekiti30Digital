"""Request/response schemas for media uploads and admin review."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UploadInitRequest(BaseModel):
    contributor: str = Field(min_length=1)
    source: str | None = None
    location_lga: str | None = None
    description: str | None = None
    rights_status: str = Field(min_length=1)
    related_content_id: str | None = None
    # Must be one of cloudinary_convention.ALLOWED_FOLDERS.
    folder: str


class UploadInitResponse(BaseModel):
    """Everything the frontend needs to upload directly to Cloudinary."""

    asset_id: int
    cloud_name: str
    upload_preset: str
    folder: str
    # Not enforceable by an unsigned preset — the frontend must check these
    # before uploading.
    max_file_bytes: int
    allowed_formats: list[str]


class UploadCompleteRequest(BaseModel):
    """The values Cloudinary returns to the browser after a direct upload."""

    public_id: str = Field(min_length=1)
    secure_url: str = Field(min_length=1)


class RejectRequest(BaseModel):
    rejection_reason: str = Field(min_length=1)


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_id: str | None
    cloudinary_url: str | None
    folder: str
    contributor: str
    source: str | None
    location_lga: str | None
    description: str | None
    rights_status: str
    related_content_id: str | None
    status: str
    rejection_reason: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
