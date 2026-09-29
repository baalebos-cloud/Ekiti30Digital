"""Timeline ingestion (app/services/timeline_ingestion.py) and GET /api/timeline."""

import os
from collections import Counter

import pytest

from app.models.timeline_event import TimelineEvent
from app.services.timeline_ingestion import ingest_timeline, is_iso_partial_date, load_csv

REAL_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", "03_Timeline", "EKITI30_Timeline_Events_1996-2026.csv"
)


def make_row(**overrides) -> dict:
    """A valid CSV row, keyed as load_csv returns it."""
    row = {
        "id": "EK-100",
        "date_display": "Jul 2010",
        "date_start": "2010-07",
        "date_end": "none",
        "date_precision": "month",
        "date_basis": "stated_by_source",
        "event_title": "An event",
        "description": "Something happened.",
        "category": "Government",
        "evidence_type": "news_report",
        "source": "A newspaper",
        "source_link": "https://example.com/story",
        "source_type": "News outlet",
        "verification_status": "Single source",
        "claim_source_map": "none",
        "unconfirmed_details": "The exact day.",
        "claims_and_disputes": "none",
        "notes_limitations": "none",
        "additional_sources": "https://example.com/a | https://example.com/b",
    }
    row.update(overrides)
    return row


# --- Ingestion ---


@pytest.mark.parametrize(
    ("value", "ok"),
    [("1996", True), ("1998-07", True), ("1999-05-29", True), ("1999-02-30", False),
     ("1999-5", False), ("none", False), ("", False)],
)
def test_is_iso_partial_date(value, ok):
    assert is_iso_partial_date(value) is ok


def test_real_csv_loads_all_50_events_with_expected_statuses(db_session):
    result = ingest_timeline(load_csv(REAL_CSV), db_session)

    assert (result.created, result.updated, result.skipped) == (50, 0, [])
    counts = Counter(e.verification_status for e in db_session.query(TimelineEvent))
    assert counts == {
        "Verified": 26,
        "Single source": 11,
        "Needs primary source": 9,
        "Conflicting sources": 4,
    }


def test_ingest_keeps_the_dataset_id_and_stores_values_as_is(db_session):
    ingest_timeline([make_row()], db_session)

    event = db_session.get(TimelineEvent, "EK-100")
    assert event.date_start == "2010-07"
    assert event.date_end == "none"
    assert event.verification_status == "Single source"


def test_rerunning_updates_in_place_without_duplicating(db_session):
    ingest_timeline([make_row()], db_session)
    result = ingest_timeline([make_row(verification_status="Verified")], db_session)

    assert (result.created, result.updated) == (0, 1)
    assert db_session.query(TimelineEvent).one().verification_status == "Verified"


def test_rerunning_the_real_csv_does_not_duplicate(db_session):
    rows = load_csv(REAL_CSV)
    ingest_timeline(rows, db_session)
    result = ingest_timeline(rows, db_session)

    assert (result.created, result.updated) == (0, 50)
    assert db_session.query(TimelineEvent).count() == 50


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"event_title": ""}, "missing required field(s): event_title"),
        # The dataset's "none" placeholder doesn't count as a value.
        ({"source": "none"}, "missing required field(s): source"),
        ({"date_start": "July 2010"}, "invalid date_start"),
        ({"date_end": "2010-13"}, "invalid date_end"),
        ({"verification_status": "Probably true"}, "unknown verification_status"),
        ({"verification_status": "verified"}, "unknown verification_status"),
    ],
)
def test_bad_rows_are_skipped_and_reported(db_session, overrides, reason):
    result = ingest_timeline([make_row(id="EK-001"), make_row(id="EK-002", **overrides)], db_session)

    assert result.created == 1
    assert len(result.skipped) == 1
    assert (result.skipped[0].line, result.skipped[0].event_id) == (3, "EK-002")
    assert reason in result.skipped[0].reason
    assert [e.id for e in db_session.query(TimelineEvent)] == ["EK-001"]


def test_rows_sharing_an_id_are_all_skipped(db_session):
    result = ingest_timeline([make_row(), make_row(event_title="Other")], db_session)

    assert result.created == 0
    assert [s.reason for s in result.skipped] == ["duplicate id 'EK-100' in batch"] * 2


# --- GET /api/timeline ---


def test_list_timeline_returns_all_50_sorted_with_status(client, db_session):
    ingest_timeline(load_csv(REAL_CSV), db_session)

    response = client.get("/api/timeline")

    assert response.status_code == 200
    events = response.json()["events"]
    assert len(events) == 50
    starts = [e["dateStart"] for e in events]
    assert starts == sorted(starts)
    # Nothing is hidden or relabelled: every status comes through as-is.
    assert Counter(e["status"] for e in events) == {
        "Verified": 26,
        "Single source": 11,
        "Needs primary source": 9,
        "Conflicting sources": 4,
    }
    # frontend/src/lib/content.ts REQUIRED_FIELDS for "timeline".
    for event in events:
        for field in ("id", "date", "title", "description", "category", "status"):
            assert isinstance(event[field], str) and event[field]


def test_list_timeline_sorts_by_date_start_then_id(client, db_session):
    ingest_timeline(
        [
            make_row(id="EK-003", date_start="2001-01-15"),
            make_row(id="EK-002", date_start="2001"),
            make_row(id="EK-001", date_start="2001-01-15"),
            make_row(id="EK-004", date_start="2000-12"),
        ],
        db_session,
    )

    ids = [e["id"] for e in client.get("/api/timeline").json()["events"]]

    assert ids == ["EK-004", "EK-002", "EK-001", "EK-003"]


def test_list_timeline_item_shape(client, db_session):
    ingest_timeline([make_row()], db_session)

    [event] = client.get("/api/timeline").json()["events"]

    assert event == {
        "id": "EK-100",
        "date": "Jul 2010",
        "dateStart": "2010-07",
        "dateEnd": None,
        "datePrecision": "month",
        "dateBasis": "stated_by_source",
        "title": "An event",
        "description": "Something happened.",
        "category": "Government",
        "status": "Single source",
        "evidenceType": "news_report",
        "source": "A newspaper",
        "sourceUrl": "https://example.com/story",
        "sourceType": "News outlet",
        "claimSourceMap": None,
        "unconfirmedDetails": "The exact day.",
        "claimsAndDisputes": None,
        "notesLimitations": None,
        "additionalSources": ["https://example.com/a", "https://example.com/b"],
    }


def test_list_timeline_empty(client):
    assert client.get("/api/timeline").json() == {"events": []}
