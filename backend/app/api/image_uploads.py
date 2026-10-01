"""The HTTP side of an admin image upload, shared by every route that takes one.

LGA images (app/api/routes/content_admin.py) and homepage images
(app/api/routes/homepage_admin.py) all read the file, upload it with
cloudinary_upload.attach_image, and map its failures to the same statuses.
On any failure the record's current image is left as it was.
"""

import logging

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.services import cloudinary_upload
from app.services.cloudinary_admin import CloudinaryNotConfigured
from app.services.cloudinary_convention import MAX_UPLOAD_BYTES

logger = logging.getLogger(__name__)

_UPLOAD_ERRORS = (
    cloudinary_upload.InvalidImage,
    CloudinaryNotConfigured,
    cloudinary_upload.CloudinaryUploadError,
)


async def read_image_upload(file: UploadFile) -> bytes:
    # One byte over the limit is enough for validate_image to report "too large".
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Choose an image to upload"
        )
    return data


def image_error(err: Exception) -> HTTPException:
    """The HTTP error for a failed image upload."""
    if isinstance(err, cloudinary_upload.InvalidImage):
        code = status.HTTP_413_CONTENT_TOO_LARGE if err.too_large else status.HTTP_422_UNPROCESSABLE_CONTENT
        return HTTPException(status_code=code, detail=str(err))
    if isinstance(err, CloudinaryNotConfigured):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image uploads aren't configured on the server",
        )
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"The image upload failed: {err}")


async def attach_uploaded_image(
    record, file: UploadFile, db: Session, *, folder: str, default_filename: str, updated_by: str, what: str
):
    """Upload `file` to `folder`, set it as `record`'s image and commit; returns the refreshed record.

    `what` names the record in logs, e.g. "LGA ado-ekiti".
    """
    data = await read_image_upload(file)
    try:
        cloudinary_upload.attach_image(
            record, data, folder=folder, filename=file.filename or default_filename, updated_by=updated_by
        )
    except _UPLOAD_ERRORS as err:
        db.rollback()
        if isinstance(err, cloudinary_upload.CloudinaryUploadError):
            logger.warning("Image upload failed for %s: %s", what, err)
        raise image_error(err) from None
    db.commit()
    db.refresh(record)
    logger.info("Admin %s set the image for %s", updated_by, what)
    return record
