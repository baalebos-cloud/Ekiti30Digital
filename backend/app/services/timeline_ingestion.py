"""Timeline dataset ingestion.

Source of truth: as of the admin content editor (see PR for
feature/admin-content-editing), the live database is the source of truth for
day-to-day corrections. The CSV remains the source of truth for bulk research
updates and verification_status changes, and re-importing it will overwrite
any live-only edits to other fields on the rows it touches (see the --force
behavior in scripts/ingest_lgas.py / ingest_timeline.py).

Loads timeline rows from CSV (03_Timeline/EKITI30_Timeline_Events_1996-2026.csv,
or an admin upload), validates them, and upserts TimelineEvent rows by the
dataset's own id (e.g. "EK-001"). The one implementation used by
scripts/ingest_timeline.py, the admin import endpoint, and admin create/edit
(via validate_rows / row_values). Values are stored as the source has them
(see app/models/timeline_event.py); nothing here changes verification_status.
"""

import csv
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import IO

from sqlalchemy.orm import Session

from app.models.timeline_event import VERIFICATION_STATUSES, TimelineEvent
from app.services.attribution import is_admin_attribution

logger = logging.getLogger(__name__)

# The dataset writes blank cells as "none" (see its data dictionary).
NONE = "none"

# Must be present, and not "none", on every row.
REQUIRED_FIELDS = (
    "id",
    "date_display",
    "date_start",
    "event_title",
    "description",
    "category",
    "source",
    "verification_status",
)

# Optional columns copied onto the model unchanged (empty -> None).
OPTIONAL_FIELDS = (
    "date_end",
    "date_precision",
    "date_basis",
    "evidence_type",
    "source_link",
    "source_type",
    "claim_source_map",
    "unconfirmed_details",
    "claims_and_disputes",
    "notes_limitations",
    "additional_sources",
)

# Every column an edit can set. `id` is the key, so it isn't editable.
EDITABLE_FIELDS = REQUIRED_FIELDS[1:] + OPTIONAL_FIELDS

# The CSV's columns in the source file's order
# (03_Timeline/EKITI30_Timeline_Events_1996-2026.csv), for the downloadable
# import template.
CSV_COLUMNS = (
    "id",
    "date_display",
    "date_start",
    "date_end",
    "date_precision",
    "date_basis",
    "event_title",
    "description",
    "category",
    "evidence_type",
    "source",
    "source_link",
    "source_type",
    "verification_status",
    "claim_source_map",
    "unconfirmed_details",
    "claims_and_disputes",
    "notes_limitations",
    "additional_sources",
)

# The template's example row. An id no real event uses, so importing the
# template unedited adds one visibly fake event rather than overwriting one.
TEMPLATE_EXAMPLE = {
    "id": "EK-EXAMPLE",
    "date_display": "1 Oct 1996",
    "date_start": "1996-10-01",
    "date_end": "none",
    "date_precision": "day",
    "date_basis": "confirmed",
    "event_title": "Example event title",
    "description": "One or two sentences describing only what the cited source supports.",
    "category": "Government",
    "evidence_type": "official_statement",
    "source": "Ekiti State Government: About Ekiti",
    "source_link": "https://www.ekitistate.gov.ng/?p=444",
    "source_type": "Government website",
    "verification_status": "Single source",
    "claim_source_map": "none",
    "unconfirmed_details": "none",
    "claims_and_disputes": "none",
    "notes_limitations": "none",
    "additional_sources": "none",
}

# date_start / date_end precisions: YYYY, YYYY-MM or YYYY-MM-DD.
_ISO_FORMATS = {4: "%Y", 7: "%Y-%m", 10: "%Y-%m-%d"}


@dataclass
class SkippedRow:
    """A CSV row that failed validation and was not ingested."""

    line: int
    event_id: str | None
    reason: str


@dataclass
class AdminEdit:
    """A row the CSV would change that was last changed by an admin."""

    key: str
    updated_by: str


@dataclass
class IngestionResult:
    """Outcome of an ingest_timeline() run (or, with dry_run, what it would do)."""

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


def read_csv(source: str | IO[str]) -> list[dict]:
    """Read timeline rows from a path or an open text stream. No validation here."""
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


def is_iso_partial_date(value: str) -> bool:
    """True for a real date written as YYYY, YYYY-MM or YYYY-MM-DD."""
    fmt = _ISO_FORMATS.get(len(value))
    if fmt is None:
        return False
    try:
        datetime.strptime(value, fmt)
    except ValueError:
        return False
    return True


def validate_rows(rows: list[dict]) -> tuple[list[dict], list[SkippedRow]]:
    """Split CSV rows into (valid, skipped).

    Checks required fields, that date_start (and date_end, unless "none") is
    an ISO date at year, month or day precision, that verification_status is
    one of the dataset's four documented values, and that id is unique
    within the batch. Rows sharing a duplicated id are all skipped, since
    there's no way to tell which one is correct. Line numbers count the
    header as line 1.
    """
    id_counts: dict[str, int] = {}
    for row in rows:
        event_id = _clean(row.get("id"))
        if event_id:
            id_counts[event_id] = id_counts.get(event_id, 0) + 1

    valid: list[dict] = []
    skipped: list[SkippedRow] = []

    for line, row in enumerate(rows, start=2):
        event_id = _clean(row.get("id"))

        missing = [
            f for f in REQUIRED_FIELDS if (_clean(row.get(f)) or NONE).lower() == NONE
        ]
        if missing:
            skipped.append(
                SkippedRow(line, event_id, f"missing required field(s): {', '.join(missing)}")
            )
            continue

        date_start = _clean(row["date_start"])
        if not is_iso_partial_date(date_start):
            skipped.append(
                SkippedRow(
                    line,
                    event_id,
                    f"invalid date_start {date_start!r} (expected YYYY, YYYY-MM or YYYY-MM-DD)",
                )
            )
            continue

        date_end = _clean(row.get("date_end")) or NONE
        if date_end.lower() != NONE and not is_iso_partial_date(date_end):
            skipped.append(
                SkippedRow(
                    line,
                    event_id,
                    f"invalid date_end {date_end!r} "
                    "(expected YYYY, YYYY-MM, YYYY-MM-DD or 'none')",
                )
            )
            continue

        status = _clean(row["verification_status"])
        if status not in VERIFICATION_STATUSES:
            skipped.append(
                SkippedRow(
                    line,
                    event_id,
                    f"unknown verification_status {status!r} "
                    f"(expected one of: {', '.join(VERIFICATION_STATUSES)})",
                )
            )
            continue

        if id_counts[event_id] > 1:
            skipped.append(SkippedRow(line, event_id, f"duplicate id {event_id!r} in batch"))
            continue

        valid.append(row)

    return valid, skipped


def row_values(row: dict) -> dict:
    """The column values a validated row stores, keyed by model attribute."""
    return {name: _clean(row.get(name)) for name in EDITABLE_FIELDS}


def row_from_model(event: TimelineEvent) -> dict:
    """A stored event as a CSV-shaped row, so an edit can be re-validated whole."""
    row = {name: getattr(event, name) or "" for name in EDITABLE_FIELDS}
    row["id"] = event.id
    return row


def _now() -> datetime:
    # Stored naive in UTC, matching the other DateTime columns.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def apply_values(event: TimelineEvent, values: dict, updated_by: str | None) -> None:
    """Write values onto an event and record who changed it and when."""
    for name, value in values.items():
        setattr(event, name, value)
    event.updated_by = updated_by
    event.updated_at = _now()


def changed_fields(event: TimelineEvent, values: dict) -> list[str]:
    return [name for name, value in values.items() if getattr(event, name) != value]


def ingest_timeline(
    rows: list[dict],
    db_session: Session,
    *,
    updated_by: str,
    dry_run: bool = False,
    protect_admin_edits: bool = False,
) -> IngestionResult:
    """Validate CSV rows and upsert the valid ones into TimelineEvent, keyed by id.

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
        logger.warning("Skipping timeline CSV line %s (%s): %s", row.line, row.event_id, row.reason)

    result = IngestionResult(skipped=skipped)

    for row in valid_rows:
        event_id = _clean(row["id"])
        values = row_values(row)
        event = db_session.get(TimelineEvent, event_id)
        if event is None:
            result.created.append(event_id)
            if not dry_run:
                event = TimelineEvent(id=event_id)
                db_session.add(event)
                apply_values(event, values, updated_by)
        elif changed_fields(event, values):
            if is_admin_attribution(event.updated_by):
                edit = AdminEdit(event_id, event.updated_by)
                result.admin_edited.append(edit)
                if protect_admin_edits:
                    result.held_back.append(edit)
                    continue
            result.updated.append(event_id)
            if not dry_run:
                apply_values(event, values, updated_by)
        else:
            result.unchanged.append(event_id)

    if dry_run:
        db_session.rollback()
    else:
        db_session.commit()
    return result
