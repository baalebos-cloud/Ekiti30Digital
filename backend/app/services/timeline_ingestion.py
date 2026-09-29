"""Timeline dataset ingestion.

Loads 03_Timeline/EKITI30_Timeline_Events_1996-2026.csv, validates it, and
upserts TimelineEvent rows by the dataset's own id (e.g. "EK-001"). Values
are stored as the source has them (see app/models/timeline_event.py);
nothing here changes verification_status.
"""

import csv
import logging
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.timeline_event import VERIFICATION_STATUSES, TimelineEvent

logger = logging.getLogger(__name__)

# The dataset writes blank cells as "none" (see its data dictionary).
NONE = "none"

# Must be present, and not "none", on every row.
_REQUIRED_FIELDS = (
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
_OPTIONAL_FIELDS = (
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

# date_start / date_end precisions: YYYY, YYYY-MM or YYYY-MM-DD.
_ISO_FORMATS = {4: "%Y", 7: "%Y-%m", 10: "%Y-%m-%d"}


@dataclass
class SkippedRow:
    """A CSV row that failed validation and was not ingested."""

    line: int
    event_id: str | None
    reason: str


@dataclass
class IngestionResult:
    """Outcome of an ingest_timeline() run."""

    created: int = 0
    updated: int = 0
    skipped: list[SkippedRow] = field(default_factory=list)

    @property
    def ingested(self) -> int:
        return self.created + self.updated


def load_csv(csv_path: str) -> list[dict]:
    """Read the timeline CSV. No validation happens here — see validate_rows()."""
    # utf-8-sig: tolerate a byte-order mark if the file is re-saved in Excel.
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _clean(value: str | None) -> str | None:
    value = (value or "").strip()
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
            f for f in _REQUIRED_FIELDS if (_clean(row.get(f)) or NONE).lower() == NONE
        ]
        if missing:
            skipped.append(
                SkippedRow(line, event_id, f"missing required field(s): {', '.join(missing)}")
            )
            continue

        date_start = row["date_start"].strip()
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

        status = row["verification_status"].strip()
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


def ingest_timeline(rows: list[dict], db_session: Session) -> IngestionResult:
    """Validate CSV rows and upsert the valid ones into TimelineEvent, keyed by id.

    Expects rows as returned by load_csv(). Re-running with the same CSV
    updates rows in place rather than duplicating them. Rows no longer in
    the CSV are left alone. Invalid rows are skipped rather than failing the
    run; the result lists them with a reason.
    """
    valid_rows, skipped = validate_rows(rows)
    for row in skipped:
        logger.warning("Skipping timeline CSV line %s (%s): %s", row.line, row.event_id, row.reason)

    result = IngestionResult(skipped=skipped)

    for row in valid_rows:
        event_id = row["id"].strip()
        event = db_session.get(TimelineEvent, event_id)
        if event is None:
            event = TimelineEvent(id=event_id)
            db_session.add(event)
            result.created += 1
        else:
            result.updated += 1

        for name in _REQUIRED_FIELDS[1:]:
            setattr(event, name, row[name].strip())
        for name in _OPTIONAL_FIELDS:
            setattr(event, name, _clean(row.get(name)))

    db_session.commit()
    return result
