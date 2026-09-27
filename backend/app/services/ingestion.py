"""Ask Ekiti knowledge base ingestion.

Infrastructure only — loads the KB manifest (13_Knowledge_Base/kb_manifest.csv),
validates it, and upserts document rows. Chunking and embedding generation
are intentionally not implemented here (see the TODO in ingest_documents).
"""

import csv
import logging
from dataclasses import dataclass, field
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDocument

logger = logging.getLogger(__name__)

# Manifest date format for last_verified, e.g. "2026-01-15".
_LAST_VERIFIED_FORMAT = "%Y-%m-%d"

# The real manifest's column names -> our internal field names. Columns not
# listed here (last_verified, ingestible, path, file_sha256, ...) already
# match and are passed through unchanged.
_MANIFEST_COLUMN_MAP = {
    "id": "doc_id",
    "category": "class_",
    "source_tier": "tier",
}

# Must be present and non-empty on every ingestible row.
_REQUIRED_FIELDS = ("doc_id", "class_", "tier", "last_verified", "ingestible")


@dataclass
class SkippedRow:
    """A manifest row that failed validation and was not ingested."""

    doc_id: str | None
    reason: str


@dataclass
class IngestionResult:
    """Outcome of an ingest_documents() run."""

    ingested: int = 0
    skipped: list[SkippedRow] = field(default_factory=list)


def _is_ingestible(row: dict) -> bool:
    return (row.get("ingestible") or "").strip().lower() == "yes"


def load_manifest(csv_path: str) -> list[dict]:
    """Read the KB manifest CSV and return only ingestible rows.

    Renames the manifest's columns to our internal names (see
    _MANIFEST_COLUMN_MAP), so returned rows are keyed by doc_id, class_,
    tier, etc. A row is included only if its `ingestible` value is "yes"
    (case-insensitive). No validation happens here — see validate_rows().
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = [
            {_MANIFEST_COLUMN_MAP.get(key, key): value for key, value in row.items()}
            for row in csv.DictReader(f)
        ]

    return [row for row in rows if _is_ingestible(row)]


def _parse_last_verified(value: str) -> date:
    return datetime.strptime(value.strip(), _LAST_VERIFIED_FORMAT).date()


def validate_rows(rows: list[dict]) -> tuple[list[dict], list[SkippedRow]]:
    """Split ingestible manifest rows into (valid, skipped).

    Checks that every required field is non-empty, that last_verified is a
    valid date, and that doc_id is unique within the batch. Rows sharing a
    duplicated doc_id are all skipped, since there's no way to tell which
    one is correct.
    """
    doc_id_counts: dict[str, int] = {}
    for row in rows:
        doc_id = (row.get("doc_id") or "").strip()
        if doc_id:
            doc_id_counts[doc_id] = doc_id_counts.get(doc_id, 0) + 1

    valid: list[dict] = []
    skipped: list[SkippedRow] = []

    for row in rows:
        doc_id = (row.get("doc_id") or "").strip() or None

        missing = [name for name in _REQUIRED_FIELDS if not (row.get(name) or "").strip()]
        if missing:
            skipped.append(
                SkippedRow(doc_id, f"missing required field(s): {', '.join(missing)}")
            )
            continue

        try:
            _parse_last_verified(row["last_verified"])
        except ValueError:
            skipped.append(
                SkippedRow(
                    doc_id,
                    f"invalid last_verified date {row['last_verified']!r} "
                    f"(expected YYYY-MM-DD)",
                )
            )
            continue

        if doc_id_counts[doc_id] > 1:
            skipped.append(SkippedRow(doc_id, f"duplicate doc_id {doc_id!r} in batch"))
            continue

        valid.append(row)

    return valid, skipped


def ingest_documents(rows: list[dict], db_session: Session) -> IngestionResult:
    """Validate manifest rows and upsert the valid ones into KnowledgeDocument.

    Expects rows as returned by load_manifest(). Creates a new
    KnowledgeDocument for a doc_id that doesn't exist yet, or updates the
    existing row's fields otherwise. Invalid rows are skipped rather than
    failing the run; the result lists them with a reason.
    """
    valid_rows, skipped = validate_rows(rows)
    for row in skipped:
        logger.warning("Skipping manifest row %s: %s", row.doc_id, row.reason)

    result = IngestionResult(skipped=skipped)

    for row in valid_rows:
        doc_id = row["doc_id"].strip()

        # TODO: source_title/source_url aren't in kb_manifest.csv — look them
        # up from the document's front matter (or elsewhere) once decided.
        missing_source = [
            name for name in ("source_title", "source_url") if not row.get(name)
        ]
        if missing_source:
            logger.info("Manifest row %s has no %s", doc_id, " or ".join(missing_source))

        document = (
            db_session.query(KnowledgeDocument).filter_by(doc_id=doc_id).one_or_none()
        )
        if document is None:
            document = KnowledgeDocument(doc_id=doc_id)
            db_session.add(document)

        document.source_title = row.get("source_title") or None
        document.source_url = row.get("source_url") or None
        document.class_ = row["class_"].strip()
        document.tier = row["tier"].strip()
        document.last_verified = _parse_last_verified(row["last_verified"])
        document.ingestible = _is_ingestible(row)
        document.path = row.get("path") or None
        document.file_sha256 = row.get("file_sha256") or None

        # TODO: chunk raw_content and generate embeddings (see
        # EMBEDDING_PROVIDER / EMBEDDING_MODEL in app/core/config.py).

        result.ingested += 1

    db_session.commit()
    return result
