"""Public response shape for GET /api/timeline.

Serialized with camelCase keys to match the frontend's `TimelineEvent` type
(frontend/src/data/timelineEvents.ts), which maps date_display -> date,
event_title -> title, verification_status -> status and source_link ->
sourceUrl. The dataset's other columns are included too.

`status` is the dataset's verification_status, unchanged. Per
03_Timeline/README_Timeline_Data_Dictionary.md, "Single source" events are
to be presented as attributed and "Needs primary source" / "Conflicting
sources" as not settled; how that looks is the frontend's decision.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.timeline_event import TimelineEvent
from app.services.timeline_ingestion import NONE


def _value(value: str | None) -> str | None:
    """The dataset writes blank cells as "none"; serve those as null."""
    if value is None or value.strip().lower() == NONE:
        return None
    return value


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    date: str
    date_start: str
    date_end: str | None
    date_precision: str | None
    date_basis: str | None
    title: str
    description: str
    category: str
    status: str
    evidence_type: str | None
    source: str
    source_url: str | None
    source_type: str | None
    claim_source_map: str | None
    unconfirmed_details: str | None
    claims_and_disputes: str | None
    notes_limitations: str | None
    additional_sources: list[str]

    @classmethod
    def from_model(cls, event: TimelineEvent) -> "TimelineEventOut":
        additional = _value(event.additional_sources) or ""
        return cls(
            id=event.id,
            date=event.date_display,
            date_start=event.date_start,
            date_end=_value(event.date_end),
            date_precision=_value(event.date_precision),
            date_basis=_value(event.date_basis),
            title=event.event_title,
            description=event.description,
            category=event.category,
            status=event.verification_status,
            evidence_type=_value(event.evidence_type),
            source=event.source,
            source_url=_value(event.source_link),
            source_type=_value(event.source_type),
            claim_source_map=_value(event.claim_source_map),
            unconfirmed_details=_value(event.unconfirmed_details),
            claims_and_disputes=_value(event.claims_and_disputes),
            notes_limitations=_value(event.notes_limitations),
            additional_sources=[url.strip() for url in additional.split("|") if url.strip()],
        )


class TimelineListResponse(BaseModel):
    events: list[TimelineEventOut]
