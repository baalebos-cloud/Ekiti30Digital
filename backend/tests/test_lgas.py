"""LGA ingestion (app/services/lga_ingestion.py) and GET /api/lgas."""

import os

import pytest

from app.models.lga import Lga
from app.services.lga_ingestion import ingest_lgas, load_csv, slugify

REAL_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "02_LGAs", "ekiti_lgas.csv")


def make_row(**overrides) -> dict:
    """A valid CSV row, keyed as load_csv returns it."""
    row = {
        "lga_name": "Ido/Osi",
        "headquarters": "Ido-Ekiti",
        "latitude": "7.846",
        "longitude": "5.183",
        "coordinate_type": "Headquarters town centre",
        "major_towns_communities": "Ido-Ekiti; Osi-Ekiti",
        "notable_places": "To be researched",
        "important_institutions": "Federal Teaching Hospital Ido-Ekiti",
        "source_1_name": "State directory",
        "source_1_type": "Official government source",
        "source_1_link": "https://example.gov/lgas",
        "source_2_name": "",
        "source_2_type": "",
        "source_2_link": "",
        "source_3_name": "",
        "source_3_type": "",
        "source_3_link": "",
        "source_date": "Not specified",
        "last_checked": "2026-09-21",
        "verification_status": "Pending",
        "limitations": "Coordinates require review",
        "owner": "Researcher",
    }
    row.update(overrides)
    return row


# --- Ingestion ---


@pytest.mark.parametrize(
    ("name", "slug"),
    [("Ido/Osi", "ido-osi"), ("Ekiti South-West", "ekiti-south-west"), ("Ado Ekiti", "ado-ekiti")],
)
def test_slugify(name, slug):
    assert slugify(name) == slug


def test_real_csv_loads_all_16_lgas_as_pending(db_session):
    result = ingest_lgas(load_csv(REAL_CSV), db_session)

    assert (result.created, result.updated, result.skipped) == (16, 0, [])
    assert db_session.query(Lga).count() == 16
    # Stored as the source has it — nothing is promoted to "Verified".
    assert {lga.verification_status for lga in db_session.query(Lga)} == {"Pending"}


def test_ingest_stores_values_as_the_source_has_them(db_session):
    ingest_lgas([make_row()], db_session)

    lga = db_session.query(Lga).one()
    assert lga.slug == "ido-osi"
    assert (lga.latitude, lga.longitude) == (7.846, 5.183)
    assert lga.notable_places == "To be researched"
    assert lga.last_checked == "2026-09-21"
    assert lga.source_2_name is None


def test_rerunning_updates_in_place_without_duplicating(db_session):
    ingest_lgas([make_row()], db_session)
    result = ingest_lgas([make_row(headquarters="Changed", verification_status="Verified")], db_session)

    assert (result.created, result.updated) == (0, 1)
    lga = db_session.query(Lga).one()
    assert (lga.headquarters, lga.verification_status) == ("Changed", "Verified")


def test_rerunning_the_real_csv_does_not_duplicate(db_session):
    rows = load_csv(REAL_CSV)
    ingest_lgas(rows, db_session)
    result = ingest_lgas(rows, db_session)

    assert (result.created, result.updated) == (0, 16)
    assert db_session.query(Lga).count() == 16


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"headquarters": "  "}, "missing required field(s): headquarters"),
        ({"verification_status": ""}, "missing required field(s): verification_status"),
        ({"latitude": "north"}, "invalid coordinates"),
        ({"longitude": "200"}, "invalid coordinates"),
        ({"lga_name": "///"}, "no letters or digits"),
    ],
)
def test_bad_rows_are_skipped_and_reported(db_session, overrides, reason):
    good = make_row(lga_name="Moba")
    result = ingest_lgas([good, make_row(**overrides)], db_session)

    assert result.created == 1
    assert len(result.skipped) == 1
    assert result.skipped[0].line == 3
    assert reason in result.skipped[0].reason
    assert [lga.slug for lga in db_session.query(Lga)] == ["moba"]


def test_rows_sharing_a_slug_are_all_skipped(db_session):
    # "Ido/Osi" and "Ido Osi" both slugify to "ido-osi".
    result = ingest_lgas([make_row(), make_row(lga_name="Ido Osi")], db_session)

    assert result.created == 0
    assert [s.reason for s in result.skipped] == ["duplicate slug 'ido-osi' in batch"] * 2
    assert db_session.query(Lga).count() == 0


# --- GET /api/lgas ---


def test_list_lgas_returns_all_16_with_verification_status(client, db_session):
    ingest_lgas(load_csv(REAL_CSV), db_session)

    response = client.get("/api/lgas")

    assert response.status_code == 200
    lgas = response.json()["lgas"]
    assert len(lgas) == 16
    assert all(lga["verificationStatus"] == "Pending" for lga in lgas)
    # frontend/src/lib/content.ts REQUIRED_FIELDS for "lgas".
    for lga in lgas:
        for field in ("slug", "name", "headquarters"):
            assert isinstance(lga[field], str) and lga[field]


def test_list_lgas_item_shape(client, db_session):
    ingest_lgas(
        [
            make_row(
                source_2_name="Coordinates reference",
                source_2_type="secondary geographic database",
                source_2_link="https://example.org/ido",
            )
        ],
        db_session,
    )

    [lga] = client.get("/api/lgas").json()["lgas"]

    assert lga == {
        "slug": "ido-osi",
        "name": "Ido/Osi",
        "headquarters": "Ido-Ekiti",
        "latitude": 7.846,
        "longitude": 5.183,
        "coordinateType": "Headquarters town centre",
        "towns": ["Ido-Ekiti", "Osi-Ekiti"],
        # "To be researched" is a placeholder, not a place.
        "notablePlaces": [],
        "institutions": ["Federal Teaching Hospital Ido-Ekiti"],
        "sources": [
            {"name": "State directory", "url": "https://example.gov/lgas", "type": "Official government source"},
            {
                "name": "Coordinates reference",
                "url": "https://example.org/ido",
                "type": "secondary geographic database",
            },
        ],
        "sourceDate": "Not specified",
        "lastChecked": "2026-09-21",
        "verificationStatus": "Pending",
        "limitations": "Coordinates require review",
        "owner": "Researcher",
    }


def test_list_lgas_empty(client):
    assert client.get("/api/lgas").json() == {"lgas": []}
