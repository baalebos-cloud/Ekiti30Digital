"""Server-side lookups against the Cloudinary Admin API.

Uses CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET, which must never reach the
frontend. Used by POST /api/uploads/{id}/complete to confirm that the
resource the browser says it uploaded really exists in our account, in the
folder recorded at init time, before we store it.

Tests mock get_resource rather than calling Cloudinary.
"""

import urllib.parse

import httpx

from app.core.config import settings

_TIMEOUT_SECONDS = 10.0


class CloudinaryNotConfigured(Exception):
    """The Admin API credentials aren't set."""


class CloudinaryLookupError(Exception):
    """Cloudinary couldn't be reached or returned an unexpected error."""


def get_resource(public_id: str, resource_type: str) -> dict | None:
    """Return Cloudinary's details for an uploaded resource, or None if it
    doesn't exist.

    `resource_type` is "image" or "video". Raises CloudinaryNotConfigured or
    CloudinaryLookupError for anything other than found / not found.
    """
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    api_key = settings.CLOUDINARY_API_KEY
    api_secret = settings.CLOUDINARY_API_SECRET
    if not (cloud_name and api_key and api_secret):
        raise CloudinaryNotConfigured

    url = (
        f"https://api.cloudinary.com/v1_1/{urllib.parse.quote(cloud_name, safe='')}"
        f"/resources/{resource_type}/upload/{urllib.parse.quote(public_id, safe='/')}"
    )
    try:
        response = httpx.get(url, auth=(api_key, api_secret), timeout=_TIMEOUT_SECONDS)
    except httpx.HTTPError as err:
        raise CloudinaryLookupError(type(err).__name__) from None

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        # Deliberately not echoing the response body into our error.
        raise CloudinaryLookupError(f"HTTP {response.status_code}")
    return response.json()


def resource_folder(resource: dict) -> str | None:
    """The folder a resource lives in.

    Accounts in dynamic folder mode report it as `asset_folder`; older
    fixed-folder accounts report `folder`.
    """
    if "asset_folder" in resource:
        return resource["asset_folder"]
    return resource.get("folder")
