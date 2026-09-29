"""LGA dataset ingestion.

Loads 02_LGAs/ekiti_lgas.csv, validates it, and upserts Lga rows by slug.
Values are stored as the source has them (see app/models/lga.py); nothing
here changes verification_status.
"""

import csv
import logging
import re
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.lga import Lga

logger = logging.getLogger(__name__)

# Must be present and non-empty on every row.
_REQUIRED_FIELDS = (
    "lga_name",
    "headquarters",
    "latitude",
    "longitude",
    "last_checked",
    "verification_status",
)

# Optional text columns copied onto the model unchanged (empty -> None).
_OPTIONAL_FIELDS = (
    "coordinate_type",
    "major_towns_communities",
    "notable_places",
    "important_institutions",
    *(f"source_{n}_{part}" for n in (1, 2, 3) for part in ("name", "type", "link")),
    "source_date",
    "limitations",
    "owner",
)


@dataclass
class SkippedRow:
    """A CSV row that failed validation and was not ingested."""

    line: int
    lga_name: str | None
    reason: str


@dataclass
class IngestionResult:
    """Outcome of an ingest_lgas() run."""

    created: int = 0
    updated: int = 0
    skipped: list[SkippedRow] = field(default_factory=list)

    @property
    def ingested(self) -> int:
        return self.created + self.updated


def slugify(name: str) -> str:
    """"Ido/Osi" -> "ido-osi", "Ekiti South-West" -> "ekiti-south-west"."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_csv(csv_path: str) -> list[dict]:
    """Read the LGA CSV. No validation happens here — see validate_rows()."""
    # utf-8-sig: tolerate a byte-order mark if the file is re-saved in Excel.
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _clean(value: str | None) -> str | None:
    value = (value or "").strip()
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
        slug = slugify(row.get("lga_name") or "")
        if slug:
            slug_counts[slug] = slug_counts.get(slug, 0) + 1

    valid: list[dict] = []
    skipped: list[SkippedRow] = []

    for line, row in enumerate(rows, start=2):
        name = _clean(row.get("lga_name"))

        missing = [f for f in _REQUIRED_FIELDS if not _clean(row.get(f))]
        if missing:
            skipped.append(SkippedRow(line, name, f"missing required field(s): {', '.join(missing)}"))
            continue

        slug = slugify(name)
        if not slug:
            skipped.append(SkippedRow(line, name, "lga_name has no letters or digits to slugify"))
            continue

        try:
            latitude = _coordinate(row["latitude"], -90, 90)
            longitude = _coordinate(row["longitude"], -180, 180)
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


def ingest_lgas(rows: list[dict], db_session: Session) -> IngestionResult:
    """Validate CSV rows and upsert the valid ones into Lga, keyed by slug.

    Expects rows as returned by load_csv(). Re-running with the same CSV
    updates rows in place rather than duplicating them. Rows no longer in
    the CSV are left alone. Invalid rows are skipped rather than failing the
    run; the result lists them with a reason.
    """
    valid_rows, skipped = validate_rows(rows)
    for row in skipped:
        logger.warning("Skipping LGA CSV line %s (%s): %s", row.line, row.lga_name, row.reason)

    result = IngestionResult(skipped=skipped)

    for row in valid_rows:
        lga = db_session.query(Lga).filter_by(slug=row["slug"]).one_or_none()
        if lga is None:
            lga = Lga(slug=row["slug"])
            db_session.add(lga)
            result.created += 1
        else:
            result.updated += 1

        lga.lga_name = row["lga_name"].strip()
        lga.headquarters = row["headquarters"].strip()
        lga.latitude = row["latitude"]
        lga.longitude = row["longitude"]
        lga.last_checked = row["last_checked"].strip()
        lga.verification_status = row["verification_status"].strip()
        for name in _OPTIONAL_FIELDS:
            setattr(lga, name, _clean(row.get(name)))

    db_session.commit()
    return result
