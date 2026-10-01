"""LGA images from a zip uploaded alongside the LGA CSV import.

Images never come from a CSV cell: each file in the zip is matched to an LGA
by its filename without extension ("ado-ekiti.jpg" -> "ado-ekiti", compared
case-insensitively) against the slugs of the rows in the same CSV. LGAs in
the CSV with no image in the zip keep their image_url as it is.

Each matched image is uploaded (app/services/cloudinary_upload.py) after the
CSV rows are saved, and committed on its own: one failed image never undoes
the rows or the other images.
"""

import io
import logging
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.models.lga import Lga
from app.services import cloudinary_upload
from app.services.cloudinary_admin import CloudinaryNotConfigured
from app.services.cloudinary_convention import MAX_UPLOAD_BYTES
from app.services.lga_ingestion import slugify

logger = logging.getLogger(__name__)

LGA_IMAGE_FOLDER = "EKITI30/LGAs"

# More than every LGA with room to spare; a zip beyond this is refused whole.
MAX_ZIP_ENTRIES = 200

ATTACHED = "attached"
WOULD_ATTACH = "would_attach"
SKIPPED = "skipped"
FAILED = "failed"


class InvalidZip(ValueError):
    """The upload isn't a readable zip, or has too many files."""


# What zipfile raises for a damaged archive or entry. Not only BadZipFile:
# bad offsets surface as ValueError ("negative seek value"), truncated data
# as EOFError/OSError, encryption as RuntimeError, odd compression as
# NotImplementedError.
_ZIP_ERRORS = (zipfile.BadZipFile, ValueError, OSError, EOFError, RuntimeError, NotImplementedError)


# Filename extensions an image in the zip may have. The content is still
# checked (cloudinary_upload.validate_image); this only reports obvious
# non-images (notes.txt) as such rather than as an unknown slug.
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


@dataclass
class ZipImage:
    filename: str
    stem: str
    data: bytes | None
    too_large: bool = False

    @property
    def extension(self) -> str:
        return self.filename.rsplit(".", 1)[1].lower() if "." in self.filename else ""


@dataclass
class ImageResult:
    filename: str
    slug: str | None
    status: str  # ATTACHED, WOULD_ATTACH, SKIPPED or FAILED
    reason: str | None = None


def _is_junk(name: str) -> bool:
    """Folders and the files macOS and Windows add to zips unasked."""
    path = PurePosixPath(name)
    return (
        name.endswith("/")
        or "__MACOSX" in path.parts
        or path.name.startswith(".")
        or path.name.lower() in {"thumbs.db", "desktop.ini"}
    )


def read_zip(data: bytes) -> list[ZipImage]:
    """The files in a zip, ignoring folders and OS junk.

    Each file is read no further than MAX_UPLOAD_BYTES + 1, whatever size
    the zip claims, so a zip bomb can't exhaust memory.
    """
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        infos = [info for info in archive.infolist() if not _is_junk(info.filename)]
    except _ZIP_ERRORS:
        raise InvalidZip("images must be a .zip file") from None
    if len(infos) > MAX_ZIP_ENTRIES:
        raise InvalidZip(f"the zip has {len(infos)} files; at most {MAX_ZIP_ENTRIES} are allowed")

    images = []
    for info in infos:
        name = PurePosixPath(info.filename).name
        stem = name.rsplit(".", 1)[0].strip().lower() if "." in name else name.strip().lower()
        if info.file_size > MAX_UPLOAD_BYTES:
            images.append(ZipImage(name, stem, None, too_large=True))
            continue
        try:
            with archive.open(info) as stream:
                content = stream.read(MAX_UPLOAD_BYTES + 1)
        except _ZIP_ERRORS:
            # Damaged, encrypted or an unsupported compression method: this
            # file is reported as unreadable; the rest of the zip still counts.
            images.append(ZipImage(name, stem, None))
            continue
        images.append(ZipImage(name, stem, content, too_large=len(content) > MAX_UPLOAD_BYTES))
    return images


def match_images(
    images: list[ZipImage], csv_slugs: set[str], skipped_slugs: set[str]
) -> tuple[list[tuple[ZipImage, str]], list[ImageResult]]:
    """Split zip images into (matched to a slug, results for the rest).

    csv_slugs are the valid rows' slugs; skipped_slugs those of rows the
    import skipped as invalid (their images are reported, not attached).
    """
    stems: dict[str, int] = {}
    for image in images:
        stems[image.stem] = stems.get(image.stem, 0) + 1

    matched: list[tuple[ZipImage, str]] = []
    results: list[ImageResult] = []
    for image in images:
        slug = slugify(image.stem)
        if image.extension not in IMAGE_EXTENSIONS:
            results.append(ImageResult(image.filename, None, SKIPPED, "not a JPG, PNG or WebP file"))
        elif not slug or slug != image.stem:
            results.append(ImageResult(image.filename, None, SKIPPED,
                                       "filename isn't an LGA slug (e.g. ado-ekiti.jpg)"))
        elif stems[image.stem] > 1:
            results.append(ImageResult(image.filename, slug, SKIPPED,
                                       f"more than one image for {slug!r} in the zip"))
        elif slug in skipped_slugs:
            results.append(ImageResult(image.filename, slug, SKIPPED,
                                       "this LGA's CSV row was skipped, so its image was too"))
        elif slug not in csv_slugs:
            results.append(ImageResult(image.filename, slug, SKIPPED,
                                       f"no LGA with slug {slug!r} in this CSV"))
        else:
            matched.append((image, slug))
    return matched, results


def attach_image(lga: Lga, data: bytes, filename: str, updated_by: str) -> None:
    """Validate, upload and record one LGA image; the caller commits.

    Raises cloudinary_upload.InvalidImage, CloudinaryNotConfigured or
    cloudinary_upload.CloudinaryUploadError, leaving the LGA unchanged.
    """
    cloudinary_upload.attach_image(
        lga, data, folder=LGA_IMAGE_FOLDER, filename=filename, updated_by=updated_by
    )


def apply_images(
    matched: list[tuple[ZipImage, str]], db: Session, *, updated_by: str, dry_run: bool
) -> list[ImageResult]:
    """Upload and attach matched images, one commit each (or, with dry_run, check them only)."""
    results = []
    for image, slug in matched:
        if image.too_large or image.data is None:
            reason = (f"image must be at most {MAX_UPLOAD_BYTES // (1024 * 1024)} MB"
                      if image.too_large else "couldn't be read from the zip")
            results.append(ImageResult(image.filename, slug, FAILED, reason))
            continue
        try:
            cloudinary_upload.validate_image(image.data)
        except cloudinary_upload.InvalidImage as err:
            results.append(ImageResult(image.filename, slug, FAILED, str(err)))
            continue
        if dry_run:
            results.append(ImageResult(image.filename, slug, WOULD_ATTACH))
            continue

        lga = db.query(Lga).filter_by(slug=slug).one_or_none()
        if lga is None:  # the row was matched but isn't stored (shouldn't happen)
            results.append(ImageResult(image.filename, slug, FAILED, "LGA not found"))
            continue
        try:
            attach_image(lga, image.data, image.filename, updated_by)
            db.commit()
        except CloudinaryNotConfigured:
            db.rollback()
            results.append(ImageResult(image.filename, slug, FAILED, "image uploads aren't configured on the server"))
            continue
        except cloudinary_upload.CloudinaryUploadError as err:
            db.rollback()
            logger.warning("LGA image upload failed for %s (%s): %s", slug, image.filename, err)
            results.append(ImageResult(image.filename, slug, FAILED, f"upload failed: {err}"))
            continue
        results.append(ImageResult(image.filename, slug, ATTACHED))
    return results


def row_slugs(valid_rows: list[dict], skipped_rows) -> tuple[set[str], set[str]]:
    """Slugs of the import's valid rows, and of its skipped rows (where they have a name)."""
    valid = {row["slug"] for row in valid_rows}
    skipped = {slugify(s.lga_name) for s in skipped_rows if s.lga_name and slugify(s.lga_name)}
    return valid, skipped - valid
