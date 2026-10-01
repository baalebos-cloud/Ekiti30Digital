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

# Folders only admin uploads (signed, through the backend:
# app/services/cloudinary_upload.py) may use, for site content an admin
# publishes directly. Never offered to member uploads, so they aren't in
# ALLOWED_FOLDERS.
HOMEPAGE_HERO_FOLDER = "EKITI30/Homepage/Hero"
HOMEPAGE_LEADERS_FOLDER = "EKITI30/Homepage/Leaders"
HOMEPAGE_LANDMARKS_FOLDER = "EKITI30/Homepage/Landmarks"
HOMEPAGE_MOMENTS_FOLDER = "EKITI30/Homepage/Moments"
ADMIN_ONLY_FOLDERS: tuple[str, ...] = (
    HOMEPAGE_HERO_FOLDER,
    HOMEPAGE_LEADERS_FOLDER,
    HOMEPAGE_LANDMARKS_FOLDER,
    HOMEPAGE_MOMENTS_FOLDER,
)

# Enforced by Cloudinary itself via the upload preset.
ALLOWED_FORMATS: tuple[str, ...] = ("jpg", "png", "webp", "mp4")

# The still-image subset, for uploads that must be images (LGA images, via
# app/services/cloudinary_upload.py).
VIDEO_FORMATS: tuple[str, ...] = ("mp4",)
IMAGE_FORMATS: tuple[str, ...] = tuple(f for f in ALLOWED_FORMATS if f not in VIDEO_FORMATS)

# Cloudinary upload presets can't enforce a file size limit, so this must
# be checked client-side before uploading (e.g. the Upload Widget's
# maxFileSize option). Exposed to the frontend via POST /api/uploads/init.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_folder(folder: str) -> bool:
    """Return True if `folder` is exactly one of ALLOWED_FOLDERS."""
    return folder in ALLOWED_FOLDERS


def validate_admin_folder(folder: str) -> bool:
    """Return True if an admin upload may go to `folder`: an allowed folder or an admin-only one."""
    return folder in ALLOWED_FOLDERS or folder in ADMIN_ONLY_FOLDERS
