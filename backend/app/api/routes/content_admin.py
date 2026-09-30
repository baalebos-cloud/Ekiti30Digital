"""Admin editing of LGAs and timeline events: create, edit, delete, CSV import.

Same pattern as app/api/routes/admin.py: every route requires a valid admin
JWT. updated_by is always the verified token's email and updated_at is set
by the server; request bodies can't set either (see
app/schemas/content_admin.py). Validation and upserts go through the
ingestion services, the same code the CLI scripts use.

Every write is also logged (who, what, which key), since deletes leave no
row behind to carry updated_by.
"""

import csv
import io
import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import AdminUser, require_admin
from app.models.base import get_db
from app.models.lga import Lga
from app.models.timeline_event import TimelineEvent
from app.schemas.content_admin import (
    ImageResultOut,
    ImportResult,
    LgaAdminOut,
    LgaCreate,
    LgaImportResult,
    LgaUpdate,
    SkippedRowOut,
    TimelineAdminOut,
    TimelineCreate,
    TimelineUpdate,
)
from app.services import cloudinary_upload, lga_images, lga_ingestion, timeline_ingestion
from app.services.cloudinary_admin import CloudinaryNotConfigured
from app.services.cloudinary_convention import MAX_UPLOAD_BYTES

logger = logging.getLogger(__name__)

# The real LGA CSV is ~10 KB and the timeline CSV ~100 KB.
MAX_IMPORT_BYTES = 2 * 1024 * 1024
# An images zip: room for a full-size image for every LGA.
MAX_ZIP_BYTES = 200 * 1024 * 1024


def _identity(admin: AdminUser) -> str:
    return admin.email.strip().lower()


def _as_text(value) -> str:
    if value is None:
        return ""
    # 200.0 -> "200", so error messages quote what the admin typed.
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _as_row(body_values: dict) -> dict:
    """Request values as CSV-shaped strings, the form validate_rows expects."""
    return {name: _as_text(value) for name, value in body_values.items()}


def _invalid(reason: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=reason)


async def _read_upload(file: UploadFile, service) -> list[dict]:
    data = await file.read(MAX_IMPORT_BYTES + 1)
    if len(data) > MAX_IMPORT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"CSV must be at most {MAX_IMPORT_BYTES // (1024 * 1024)} MB",
        )
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise _invalid("CSV must be UTF-8 encoded") from None

    rows = service.read_csv(io.StringIO(text, newline=""))
    if not rows:
        raise _invalid("CSV has no data rows")
    missing = service.missing_columns(rows)
    if missing:
        raise _invalid(f"CSV is missing required column(s): {', '.join(missing)}")
    return rows


def _import_result(result, dry_run: bool, key_attr: str) -> ImportResult:
    return ImportResult(
        dry_run=dry_run,
        created=result.created,
        updated=result.updated,
        unchanged=result.unchanged,
        skipped=[
            SkippedRowOut(line=s.line, key=getattr(s, key_attr), reason=s.reason)
            for s in result.skipped
        ],
    )


def _csv_download(columns: tuple[str, ...], example: dict[str, str], filename: str) -> Response:
    """A one-example-row CSV as a file download.

    UTF-8 with a byte-order mark so Excel opens it correctly; the importers
    accept the mark.
    """
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\r\n")
    writer.writeheader()
    writer.writerow(example)
    return Response(
        content="﻿" + out.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _read_image_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise _invalid("Choose an image to upload")
    return data


def _image_error(err: Exception) -> HTTPException:
    """The HTTP error for a failed image upload — the image_url stays as it was."""
    if isinstance(err, cloudinary_upload.InvalidImage):
        code = status.HTTP_413_CONTENT_TOO_LARGE if err.too_large else status.HTTP_422_UNPROCESSABLE_CONTENT
        return HTTPException(status_code=code, detail=str(err))
    if isinstance(err, CloudinaryNotConfigured):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image uploads aren't configured on the server",
        )
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"The image upload failed: {err}")


# --- LGAs ---

lgas_router = APIRouter(
    prefix="/api/admin/lgas", tags=["admin"], dependencies=[Depends(require_admin)]
)


def _get_lga(slug: str, db: Session) -> Lga:
    lga = db.query(Lga).filter_by(slug=slug).one_or_none()
    if lga is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LGA not found")
    return lga


def _validated_lga(row: dict) -> dict:
    valid, skipped = lga_ingestion.validate_rows([row])
    if skipped:
        raise _invalid(skipped[0].reason)
    return lga_ingestion.row_values(valid[0])


@lgas_router.get("", response_model=list[LgaAdminOut])
def list_lgas(db: Session = Depends(get_db)):
    """Every LGA with its stored columns and who last changed it."""
    return db.query(Lga).order_by(Lga.slug).all()


@lgas_router.post("", response_model=LgaAdminOut, status_code=status.HTTP_201_CREATED)
def create_lga(
    body: LgaCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    values = _validated_lga(_as_row(body.model_dump()))
    if db.query(Lga).filter_by(slug=values["slug"]).one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An LGA with slug {values['slug']!r} already exists",
        )
    lga = Lga()
    db.add(lga)
    lga_ingestion.apply_values(lga, values, _identity(admin))
    db.commit()
    db.refresh(lga)
    logger.info("Admin %s created LGA %s", _identity(admin), lga.slug)
    return lga


@lgas_router.patch("/{slug}", response_model=LgaAdminOut)
def update_lga(
    slug: str,
    body: LgaUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Change the fields sent. Renaming changes the slug, as ingestion would."""
    lga = _get_lga(slug, db)
    row = lga_ingestion.row_from_model(lga)
    row.update(_as_row(body.model_dump(exclude_unset=True)))
    values = _validated_lga(row)

    if values["slug"] != slug and db.query(Lga).filter_by(slug=values["slug"]).one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An LGA with slug {values['slug']!r} already exists",
        )
    changed = lga_ingestion.changed_fields(lga, values)
    if changed:
        lga_ingestion.apply_values(lga, values, _identity(admin))
        db.commit()
        db.refresh(lga)
        logger.info("Admin %s updated LGA %s: %s", _identity(admin), slug, ", ".join(changed))
    return lga


@lgas_router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lga(
    slug: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    lga = _get_lga(slug, db)
    db.delete(lga)
    db.commit()
    logger.info("Admin %s deleted LGA %s", _identity(admin), slug)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@lgas_router.get("/template.csv")
def lga_template():
    """An import template: the LGA CSV's columns and one example row (no image column)."""
    return _csv_download(lga_ingestion.CSV_COLUMNS, lga_ingestion.TEMPLATE_EXAMPLE, "lga-import-template.csv")


@lgas_router.post("/import", response_model=LgaImportResult)
async def import_lgas(
    file: UploadFile = File(..., description="The LGA CSV"),
    images: UploadFile | None = File(None, description="Optional zip of images named <slug>.jpg/.png/.webp"),
    dry_run: bool = Query(False, description="Report what would change without writing"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Upsert LGAs from an uploaded CSV, with the CLI script's exact rules.

    With an images zip, each image named after a slug in this CSV is
    uploaded and attached once the rows are saved; images that match no row
    are reported, and LGAs with no image in the zip keep theirs. A failed
    image never undoes the rows.
    """
    rows = await _read_upload(file, lga_ingestion)

    zip_images: list[lga_images.ZipImage] = []
    if images is not None and images.filename:
        data = await images.read(MAX_ZIP_BYTES + 1)
        if len(data) > MAX_ZIP_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"The images zip must be at most {MAX_ZIP_BYTES // (1024 * 1024)} MB",
            )
        if data:
            try:
                zip_images = lga_images.read_zip(data)
            except lga_images.InvalidZip as err:
                raise _invalid(str(err)) from None

    # Match against this CSV's rows before anything is written.
    valid_rows, invalid_rows = lga_ingestion.validate_rows(rows)
    csv_slugs, skipped_slugs = lga_images.row_slugs(valid_rows, invalid_rows)
    matched, image_results = lga_images.match_images(zip_images, csv_slugs, skipped_slugs)

    result = lga_ingestion.ingest_lgas(rows, db, updated_by=_identity(admin), dry_run=dry_run)
    image_results += lga_images.apply_images(matched, db, updated_by=_identity(admin), dry_run=dry_run)
    order = {image.filename: i for i, image in enumerate(zip_images)}
    image_results.sort(key=lambda r: order.get(r.filename, 0))

    if not dry_run:
        logger.info(
            "Admin %s imported LGAs: %d created, %d updated, %d unchanged, %d skipped; images: %d attached, %d not",
            _identity(admin), len(result.created), len(result.updated), len(result.unchanged),
            len(result.skipped), sum(r.status == lga_images.ATTACHED for r in image_results),
            sum(r.status != lga_images.ATTACHED for r in image_results),
        )
    base = _import_result(result, dry_run, "lga_name")
    return LgaImportResult(
        **base.model_dump(),
        images=[ImageResultOut(filename=r.filename, slug=r.slug, status=r.status, reason=r.reason) for r in image_results],
    )


@lgas_router.post("/{slug}/image", response_model=LgaAdminOut)
async def upload_lga_image(
    slug: str,
    file: UploadFile = File(..., description="A JPG, PNG or WebP image"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Upload an image for an existing LGA (create the LGA first) and set its image_url.

    On any failure the LGA's current image is left as it was.
    """
    lga = _get_lga(slug, db)
    data = await _read_image_upload(file)
    try:
        lga_images.attach_image(lga, data, file.filename or f"{slug}.jpg", _identity(admin))
    except (cloudinary_upload.InvalidImage, CloudinaryNotConfigured, cloudinary_upload.CloudinaryUploadError) as err:
        db.rollback()
        if isinstance(err, cloudinary_upload.CloudinaryUploadError):
            logger.warning("LGA image upload failed for %s: %s", slug, err)
        raise _image_error(err) from None
    db.commit()
    db.refresh(lga)
    logger.info("Admin %s set the image for LGA %s", _identity(admin), slug)
    return lga


# --- Timeline ---

timeline_router = APIRouter(
    prefix="/api/admin/timeline", tags=["admin"], dependencies=[Depends(require_admin)]
)


def _get_event(event_id: str, db: Session) -> TimelineEvent:
    event = db.get(TimelineEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found")
    return event


def _validated_event(row: dict) -> dict:
    valid, skipped = timeline_ingestion.validate_rows([row])
    if skipped:
        raise _invalid(skipped[0].reason)
    return timeline_ingestion.row_values(valid[0])


@timeline_router.get("/template.csv")
def timeline_template():
    """An import template: the timeline CSV's columns and one example row."""
    return _csv_download(
        timeline_ingestion.CSV_COLUMNS, timeline_ingestion.TEMPLATE_EXAMPLE, "timeline-import-template.csv"
    )


@timeline_router.get("", response_model=list[TimelineAdminOut])
def list_events(db: Session = Depends(get_db)):
    """Every event with its stored columns and who last changed it, oldest first."""
    return sorted(db.query(TimelineEvent).all(), key=lambda e: (e.date_start, e.id))


@timeline_router.post("", response_model=TimelineAdminOut, status_code=status.HTTP_201_CREATED)
def create_event(
    body: TimelineCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    row = _as_row(body.model_dump())
    values = _validated_event(row)
    event_id = row["id"].strip()
    if db.get(TimelineEvent, event_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A timeline event with id {event_id!r} already exists",
        )
    event = TimelineEvent(id=event_id)
    db.add(event)
    timeline_ingestion.apply_values(event, values, _identity(admin))
    db.commit()
    db.refresh(event)
    logger.info("Admin %s created timeline event %s", _identity(admin), event_id)
    return event


@timeline_router.patch("/{event_id}", response_model=TimelineAdminOut)
def update_event(
    event_id: str,
    body: TimelineUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = _get_event(event_id, db)
    row = timeline_ingestion.row_from_model(event)
    row.update(_as_row(body.model_dump(exclude_unset=True)))
    values = _validated_event(row)

    changed = timeline_ingestion.changed_fields(event, values)
    if changed:
        timeline_ingestion.apply_values(event, values, _identity(admin))
        db.commit()
        db.refresh(event)
        logger.info(
            "Admin %s updated timeline event %s: %s", _identity(admin), event_id, ", ".join(changed)
        )
    return event


@timeline_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    event = _get_event(event_id, db)
    db.delete(event)
    db.commit()
    logger.info("Admin %s deleted timeline event %s", _identity(admin), event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@timeline_router.post("/import", response_model=ImportResult)
async def import_events(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="Report what would change without writing"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Upsert timeline events from an uploaded CSV, with the CLI script's exact rules."""
    rows = await _read_upload(file, timeline_ingestion)
    result = timeline_ingestion.ingest_timeline(
        rows, db, updated_by=_identity(admin), dry_run=dry_run
    )
    if not dry_run:
        logger.info(
            "Admin %s imported timeline: %d created, %d updated, %d unchanged, %d skipped",
            _identity(admin), len(result.created), len(result.updated),
            len(result.unchanged), len(result.skipped),
        )
    return _import_result(result, dry_run, "event_id")
