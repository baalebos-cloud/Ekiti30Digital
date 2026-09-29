"""Ekiti timeline events, loaded from 03_Timeline/EKITI30_Timeline_Events_1996-2026.csv.

Columns mirror the CSV (see 03_Timeline/README_Timeline_Data_Dictionary.md)
and are stored as the source has them, including its `none` placeholder for
blank cells. Loaded by app/services/timeline_ingestion.py.

verification_status is stored and served unchanged. Per the data dictionary,
"Single source" events must be presented as attributed, and "Needs primary
source" / "Conflicting sources" must not be presented as settled — that's a
display decision for the frontend, so nothing here filters on it.
"""

from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

VERIFICATION_STATUSES = (
    "Verified",
    "Single source",
    "Needs primary source",
    "Conflicting sources",
)


class TimelineEvent(Base):
    """One event row from the source dataset."""

    __tablename__ = "timeline_events"

    # The dataset's stable ID, e.g. "EK-001". Never renumbered.
    id: Mapped[str] = mapped_column(primary_key=True)

    date_display: Mapped[str]
    # ISO 8601 at the event's precision: YYYY, YYYY-MM or YYYY-MM-DD, so it
    # sorts correctly as text. date_end is "none" for single dates.
    date_start: Mapped[str] = mapped_column(index=True)
    date_end: Mapped[str | None]
    date_precision: Mapped[str | None]
    date_basis: Mapped[str | None] = mapped_column(Text)

    event_title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str]

    evidence_type: Mapped[str | None]
    source: Mapped[str]
    source_link: Mapped[str | None]
    source_type: Mapped[str | None]

    # One of VERIFICATION_STATUSES.
    verification_status: Mapped[str] = mapped_column(index=True)

    claim_source_map: Mapped[str | None] = mapped_column(Text)
    unconfirmed_details: Mapped[str | None] = mapped_column(Text)
    claims_and_disputes: Mapped[str | None] = mapped_column(Text)
    notes_limitations: Mapped[str | None] = mapped_column(Text)
    # URLs separated by " | " in the source.
    additional_sources: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
