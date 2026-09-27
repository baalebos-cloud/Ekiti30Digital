"""Cloudinary folder and upload conventions — the single source of truth.

Every Cloudinary asset uploaded for EKITI@30 lives under one of the
top-level folders in ALLOWED_FOLDERS. Other devs: import from here instead
of hardcoding folder strings (or size/format limits) anywhere else, so the
convention only ever changes in one place.

Used by:
- app/api/routes/uploads.py — rejects upload requests for any other folder
- scripts/setup_cloudinary_preset.py — configures the unsigned preset's
  allowed formats

Note: an unsigned upload preset can't restrict which folder a direct upload
goes to (the folder is a per-upload parameter), so validate_folder() only
guards what our backend records — it doesn't stop someone holding the
preset name from uploading elsewhere in Cloudinary. Admin review before
anything is shown publicly (see app/services/assets.py) is the real gate.
"""

ALLOWED_FOLDERS: tuple[str, ...] = (
    "EKITI30/Historical",
    "EKITI30/LGAs",
    "EKITI30/Culture_Tourism",
    "EKITI30/Community_Stories",
    "EKITI30/Ekiti_2056",
)

# Enforced by Cloudinary itself via the upload preset.
ALLOWED_FORMATS: tuple[str, ...] = ("jpg", "png", "webp", "mp4")

# Cloudinary upload presets can't enforce a file size limit, so this must
# be checked client-side before uploading (e.g. the Upload Widget's
# maxFileSize option). Exposed to the frontend via POST /api/uploads/init.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_folder(folder: str) -> bool:
    """Return True if `folder` is exactly one of ALLOWED_FOLDERS."""
    return folder in ALLOWED_FOLDERS
