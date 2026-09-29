"""LGA dataset ingestion.

Source of truth: as of the admin content editor (see PR for
feature/admin-content-editing), the live database is the source of truth for
day-to-day corrections. The CSV remains the source of truth for bulk research
updates and verification_status changes, and re-importing it will overwrite
any live-only edits to other fields on the rows it touches (see the --force
behavior in scripts/ingest_lgas.py / ingest_timeline.py).

Loads LGA rows from CSV (02_LGAs/ekiti_lgas.csv, or an admin upload),
validates them, and upserts Lga rows by slug. The one implementation used by
scripts/ingest_lgas.py, the admin import endpoint, and admin create/edit (via
validate_rows / row_values). Values are stored as the source has them (see
app/models/lga.py); nothing here changes verification_status.
"""

import csv
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import IO

from sqlalchemy.orm import Session

from app.models.lga import Lga
from app.services.attribution import is_admin_attribution

logger = logging.getLogger(__name__)

# Must be present and non-empty on every row.
REQUIRED_FIELDS = (
    "lga_name",
    "headquarters",
    "latitude",
    "longitude",
    "last_checked",
    "verification_status",
)

# Optional text columns copied onto the model unchanged (empty -> None).
OPTIONAL_FIELDS = (
    "coordinate_type",
    "major_towns_communities",
    "notable_places",
    "important_institutions",
    *(f"source_{n}_{part}" for n in (1, 2, 3) for part in ("name", "type", "link")),
    "source_date",
    "limitations",
    "owner",
)

# Every column a CSV row (or admin edit) can set.
EDITABLE_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS


@dataclass
class SkippedRow:
    """A CSV row that failed validation and was not ingested."""

    line: int
    lga_name: str | None
    reason: str


@dataclass
class AdminEdit:
    """A row the CSV would change that was last changed by an admin."""

    key: str
    updated_by: str


@dataclass
class IngestionResult:
    """Outcome of an ingest_lgas() run (or, with dry_run, what it would do)."""

    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    # Valid rows identical to what's stored: left alone, not re-stamped.
    unchanged: list[str] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)
    # Changed rows whose last change was an admin's. Overwritten (and also
    # listed in `updated`) unless protect_admin_edits held them back.
    admin_edited: list[AdminEdit] = field(default_factory=list)
    # With protect_admin_edits: the admin-edited rows left untouched.
    held_back: list[AdminEdit] = field(default_factory=list)

    @property
    def ingested(self) -> int:
        return len(self.created) + len(self.updated)


def slugify(name: str) -> str:
    """"Ido/Osi" -> "ido-osi", "Ekiti South-West" -> "ekiti-south-west"."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def read_csv(source: str | IO[str]) -> list[dict]:
    """Read LGA rows from a path or an open text stream. No validation here."""
    if isinstance(source, str):
        # utf-8-sig: tolerate a byte-order mark if the file is re-saved in Excel.
        with open(source, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    return list(csv.DictReader(source))


# The CLI's original name for read_csv.
load_csv = read_csv


def missing_columns(rows: list[dict]) -> list[str]:
    """Required columns absent from the CSV header (e.g. the wrong file)."""
    header = set(rows[0]) if rows else set()
    return [name for name in REQUIRED_FIELDS if name not in header]


def _clean(value) -> str | None:
    value = ("" if value is None else str(value)).strip()
    return value or None


def _coordinate(value: str, low: float, high: float) -> float:
    number = float(value)
    if not low <= number <= high:
        raise ValueError
    return number


def validate_rows(rows: list[dict]) -> tuple[list[dict], list[SkippedRow]]:
    """Split CSV rows into (valid, skipped).

    Checks required fields, that latitude/longitude are numbers in range,
    and that each lga_name's slug is unique within the batch. Rows sharing a
    duplicated slug are all skipped, since there's no way to tell which one
    is correct. Valid rows come back with `slug`, `latitude` and `longitude`
    already parsed. Line numbers count the header as line 1.
    """
    slug_counts: dict[str, int] = {}
    for row in rows:
        slug = slugify(_clean(row.get("lga_name")) or "")
        if slug:
            slug_counts[slug] = slug_counts.get(slug, 0) + 1

    valid: list[dict] = []
    skipped: list[SkippedRow] = []

    for line, row in enumerate(rows, start=2):
        name = _clean(row.get("lga_name"))

        missing = [f for f in REQUIRED_FIELDS if not _clean(row.get(f))]
        if missing:
            skipped.append(SkippedRow(line, name, f"missing required field(s): {', '.join(missing)}"))
            continue

        slug = slugify(name)
        if not slug:
            skipped.append(SkippedRow(line, name, "lga_name has no letters or digits to slugify"))
            continue

        try:
            latitude = _coordinate(_clean(row["latitude"]), -90, 90)
            longitude = _coordinate(_clean(row["longitude"]), -180, 180)
        except ValueError:
            skipped.append(
                SkippedRow(
                    line,
                    name,
                    f"invalid coordinates {row['latitude']!r}, {row['longitude']!r} "
                    "(expected decimal degrees)",
                )
            )
            continue

        if slug_counts[slug] > 1:
            skipped.append(SkippedRow(line, name, f"duplicate slug {slug!r} in batch"))
            continue

        valid.append({**row, "slug": slug, "latitude": latitude, "longitude": longitude})

    return valid, skipped


def row_values(row: dict) -> dict:
    """The column values a validated row stores, keyed by model attribute."""
    values = {name: _clean(row.get(name)) for name in EDITABLE_FIELDS}
    values["slug"] = row["slug"]
    values["latitude"] = row["latitude"]
    values["longitude"] = row["longitude"]
    return values


def row_from_model(lga: Lga) -> dict:
    """A stored Lga as a CSV-shaped row, so an edit can be re-validated whole."""
    return {name: "" if getattr(lga, name) is None else str(getattr(lga, name)) for name in EDITABLE_FIELDS}


def _now() -> datetime:
    # Stored naive in UTC, matching the other DateTime columns.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def apply_values(lga: Lga, values: dict, updated_by: str | None) -> None:
    """Write values onto an Lga and record who changed it and when."""
    for name, value in values.items():
        setattr(lga, name, value)
    lga.updated_by = updated_by
    lga.updated_at = _now()


def changed_fields(lga: Lga, values: dict) -> list[str]:
    return [name for name, value in values.items() if getattr(lga, name) != value]


def ingest_lgas(
    rows: list[dict],
    db_session: Session,
    *,
    updated_by: str,
    dry_run: bool = False,
    protect_admin_edits: bool = False,
) -> IngestionResult:
    """Validate CSV rows and upsert the valid ones into Lga, keyed by slug.

    Expects rows as returned by read_csv(). A row whose values all match
    what's stored is counted as unchanged and not written, so re-running the
    same CSV changes nothing. Rows no longer in the CSV are left alone.
    Invalid rows are skipped rather than failing the run; the result lists
    them with a reason.

    Every created or changed row gets updated_by — the importing admin's
    verified email, or the CLI's "cli:<user>" marker (see
    app/services/attribution.py) — and updated_at.

    Changed rows last changed by an admin are listed in admin_edited. With
    protect_admin_edits (the CLI without --force) they are held back rather
    than overwritten. With dry_run, nothing is written and the result says
    what would happen.
    """
    valid_rows, skipped = validate_rows(rows)
    for row in skipped:
        logger.warning("Skipping LGA CSV line %s (%s): %s", row.line, row.lga_name, row.reason)

    result = IngestionResult(skipped=skipped)

    for row in valid_rows:
        values = row_values(row)
        slug = values["slug"]
        lga = db_session.query(Lga).filter_by(slug=slug).one_or_none()
        if lga is None:
            result.created.append(slug)
            if not dry_run:
                lga = Lga()
                db_session.add(lga)
                apply_values(lga, values, updated_by)
        elif changed_fields(lga, values):
            if is_admin_attribution(lga.updated_by):
                edit = AdminEdit(slug, lga.updated_by)
                result.admin_edited.append(edit)
                if protect_admin_edits:
                    result.held_back.append(edit)
                    continue
            result.updated.append(slug)
            if not dry_run:
                apply_values(lga, values, updated_by)
        else:
            result.unchanged.append(slug)

    if dry_run:
        db_session.rollback()
    else:
        db_session.commit()
    return result
