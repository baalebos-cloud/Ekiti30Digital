"""Server-side, signed image uploads to Cloudinary, for admins.

Unlike member uploads (app/api/routes/uploads.py: the browser uploads with
an unsigned preset and the backend verifies afterwards, because members
aren't trusted), admin uploads come through the backend and are signed with
CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET, which never leave the server.

A direct call to Cloudinary's Upload API over httpx rather than the
Cloudinary SDK: httpx is already a dependency, app/services/cloudinary_admin.py
already talks to Cloudinary this way, and a signed upload is one POST.

Every upload gets a new, Cloudinary-generated public_id. Nothing is
overwritten, so a bad replacement never destroys the previous image (which
stays in Cloudinary; nothing here deletes it).

attach_image() is the one way an admin upload lands on a record (an LGA, or
a homepage hero image, leader, landmark or moment): validate, upload, then
set the record's image_url / updated_by / updated_at.

Tests mock httpx.post rather than calling Cloudinary.
"""

import hashlib
import time
import urllib.parse
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.cloudinary_admin import CloudinaryNotConfigured
from app.services.cloudinary_convention import IMAGE_FORMATS, MAX_UPLOAD_BYTES, validate_admin_folder

_TIMEOUT_SECONDS = 60.0


class InvalidImage(ValueError):
    """The file isn't an allowed image (format), or is too large (too_large)."""

    def __init__(self, message: str, *, too_large: bool = False):
        super().__init__(message)
        self.too_large = too_large


class CloudinaryUploadError(Exception):
    """Cloudinary couldn't be reached, refused the upload, or replied oddly."""


def detect_image_format(data: bytes) -> str | None:
    """jpg / png / webp from the file's first bytes, or None."""
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def validate_image(data: bytes) -> str:
    """Return the image's format, or raise InvalidImage.

    Checked by content, not by filename, against IMAGE_FORMATS and
    MAX_UPLOAD_BYTES (app/services/cloudinary_convention.py).
    """
    if len(data) > MAX_UPLOAD_BYTES:
        raise InvalidImage(
            f"image must be at most {MAX_UPLOAD_BYTES // (1024 * 1024)} MB", too_large=True
        )
    fmt = detect_image_format(data)
    if fmt not in IMAGE_FORMATS:
        raise InvalidImage(f"image must be one of: {', '.join(IMAGE_FORMATS).upper()}")
    return fmt


def sign(params: dict[str, str], api_secret: str) -> str:
    """Cloudinary's signature: SHA-1 of the sorted params plus the secret."""
    to_sign = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hashlib.sha1(f"{to_sign}{api_secret}".encode()).hexdigest()


def upload_image(data: bytes, *, folder: str, filename: str) -> str:
    """Upload an already-validated image and return its secure_url.

    Raises CloudinaryNotConfigured, or CloudinaryUploadError for anything
    Cloudinary didn't accept.
    """
    if not validate_admin_folder(folder):
        raise ValueError(f"not an allowed folder: {folder!r}")
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    api_key = settings.CLOUDINARY_API_KEY
    api_secret = settings.CLOUDINARY_API_SECRET
    if not (cloud_name and api_key and api_secret):
        raise CloudinaryNotConfigured

    params = {
        # Cloudinary enforces this too, not just our own check.
        "allowed_formats": ",".join(IMAGE_FORMATS),
        "folder": folder,
        "timestamp": str(int(time.time())),
    }
    url = f"https://api.cloudinary.com/v1_1/{urllib.parse.quote(cloud_name, safe='')}/image/upload"
    try:
        response = httpx.post(
            url,
            data={**params, "api_key": api_key, "signature": sign(params, api_secret)},
            files={"file": (filename, data)},
            timeout=_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as err:
        raise CloudinaryUploadError(type(err).__name__) from None

    if response.status_code != 200:
        # Cloudinary's own message is safe to report (e.g. "Invalid image
        # file"); it never contains our credentials.
        try:
            message = response.json()["error"]["message"]
        except Exception:
            message = f"HTTP {response.status_code}"
        raise CloudinaryUploadError(message)

    body = response.json()
    secure_url = body.get("secure_url")
    if not (isinstance(secure_url, str) and secure_url.startswith("https://")):
        raise CloudinaryUploadError("upload response had no secure_url")
    if body.get("format") not in IMAGE_FORMATS:
        raise CloudinaryUploadError(f"Cloudinary stored an unexpected format: {body.get('format')!r}")
    return secure_url


def attach_image(record, data: bytes, *, folder: str, filename: str, updated_by: str) -> None:
    """Validate and upload `data`, then point `record` at it; the caller commits.

    `record` is any model with image_url, updated_by and updated_at columns.
    Raises InvalidImage, CloudinaryNotConfigured or CloudinaryUploadError,
    leaving the record unchanged.
    """
    validate_image(data)
    url = upload_image(data, folder=folder, filename=filename)
    record.image_url = url
    record.updated_by = updated_by
    # Naive UTC, like the models' server-side func.now().
    record.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
