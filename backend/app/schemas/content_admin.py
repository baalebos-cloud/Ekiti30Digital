"""Schemas for admin editing of LGAs and timeline events.

Admin endpoints work on the stored columns as the source CSVs name them (not
the public camelCase shapes in app/schemas/lgas.py and timeline.py), so an
admin edits exactly what's stored and a CSV import means the same thing.

Request models forbid unknown fields: updated_by and updated_at are set by
the server from the verified admin token, and a request that tries to send
them (or slug / id, which are keys) is rejected rather than silently
ignored.

verification_status can be set when creating a record, and by CSV import
(the research team's channel), but not by a live single-item edit: the
PATCH models leave it out, so sending it is rejected like the fields above. Field-level rules (required fields, coordinates, ISO dates,
verification_status values, unique keys) are the ingestion services'
validate_rows(), so edits, creates and imports can't disagree.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.timeline_event import VERIFICATION_STATUSES

_Status = Literal[*VERIFICATION_STATUSES]


class _Request(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- LGAs ---


class _LgaFields(_Request):
    """Every LGA field an admin may send, except verification_status."""

    lga_name: str | None = None
    headquarters: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    coordinate_type: str | None = None
    major_towns_communities: str | None = None
    notable_places: str | None = None
    important_institutions: str | None = None
    source_1_name: str | None = None
    source_1_type: str | None = None
    source_1_link: str | None = None
    source_2_name: str | None = None
    source_2_type: str | None = None
    source_2_link: str | None = None
    source_3_name: str | None = None
    source_3_type: str | None = None
    source_3_link: str | None = None
    source_date: str | None = None
    last_checked: str | None = None
    limitations: str | None = None
    owner: str | None = None


class LgaUpdate(_LgaFields):
    """PATCH body: only the fields sent are changed. null clears an optional field.

    No verification_status: that changes only via create or CSV import.
    """


class LgaCreate(_LgaFields):
    """POST body. The slug is derived from lga_name, as in ingestion."""

    lga_name: str
    headquarters: str
    latitude: float
    longitude: float
    last_checked: str
    verification_status: str


class LgaAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    lga_name: str
    headquarters: str
    latitude: float
    longitude: float
    coordinate_type: str | None
    major_towns_communities: str | None
    notable_places: str | None
    important_institutions: str | None
    source_1_name: str | None
    source_1_type: str | None
    source_1_link: str | None
    source_2_name: str | None
    source_2_type: str | None
    source_2_link: str | None
    source_3_name: str | None
    source_3_type: str | None
    source_3_link: str | None
    source_date: str | None
    last_checked: str
    verification_status: str
    limitations: str | None
    owner: str | None
    created_at: datetime
    updated_at: datetime
    updated_by: str | None


# --- Timeline ---


class _TimelineFields(_Request):
    """Every timeline field an admin may send, except id and verification_status."""

    date_display: str | None = None
    date_start: str | None = None
    date_end: str | None = None
    date_precision: str | None = None
    date_basis: str | None = None
    event_title: str | None = None
    description: str | None = None
    category: str | None = None
    evidence_type: str | None = None
    source: str | None = None
    source_link: str | None = None
    source_type: str | None = None
    claim_source_map: str | None = None
    unconfirmed_details: str | None = None
    claims_and_disputes: str | None = None
    notes_limitations: str | None = None
    additional_sources: str | None = None


class TimelineUpdate(_TimelineFields):
    """PATCH body: only the fields sent are changed.

    No id (it's the key) and no verification_status (that changes only via
    create or CSV import).
    """


class TimelineCreate(_TimelineFields):
    id: str
    date_display: str
    date_start: str
    event_title: str
    description: str
    category: str
    source: str
    verification_status: _Status


class TimelineAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date_display: str
    date_start: str
    date_end: str | None
    date_precision: str | None
    date_basis: str | None
    event_title: str
    description: str
    category: str
    evidence_type: str | None
    source: str
    source_link: str | None
    source_type: str | None
    verification_status: str
    claim_source_map: str | None
    unconfirmed_details: str | None
    claims_and_disputes: str | None
    notes_limitations: str | None
    additional_sources: str | None
    created_at: datetime
    updated_at: datetime
    updated_by: str | None


# --- CSV import ---


class SkippedRowOut(BaseModel):
    line: int
    # The row's slug-source name (LGAs) or id (timeline), if it had one.
    key: str | None
    reason: str


class ImportResult(BaseModel):
    """What an import did — or, with dry_run, what it would do."""

    dry_run: bool
    created: list[str]
    updated: list[str]
    unchanged: list[str]
    skipped: list[SkippedRowOut]
