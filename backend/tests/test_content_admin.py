"""Admin editing of LGAs and timeline events (app/api/routes/content_admin.py)."""

import csv
import io
import os

import pytest

from app.models.lga import Lga
from app.models.timeline_event import TimelineEvent
from app.services import lga_ingestion, timeline_ingestion

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
LGA_CSV = os.path.join(REPO, "02_LGAs", "ekiti_lgas.csv")
TIMELINE_CSV = os.path.join(REPO, "03_Timeline", "EKITI30_Timeline_Events_1996-2026.csv")


def headers(make_token, email="editor@example.com", role="admin"):
    return {"Authorization": f"Bearer {make_token(role=role, email=email)}"}


def lga_body(**overrides) -> dict:
    body = {
        "lga_name": "Test LGA",
        "headquarters": "Test-Ekiti",
        "latitude": 7.5,
        "longitude": 5.2,
        "last_checked": "2026-09-29",
        "verification_status": "Pending",
        "notable_places": "A park; A palace",
    }
    body.update(overrides)
    return body


def event_body(**overrides) -> dict:
    body = {
        "id": "EK-900",
        "date_display": "Jan 2027",
        "date_start": "2027-01",
        "event_title": "A test event",
        "description": "Something happened.",
        "category": "Government",
        "source": "A newspaper",
        "source_link": "https://example.com/story",
        "verification_status": "Single source",
    }
    body.update(overrides)
    return body


def csv_upload(rows: list[dict], fieldnames: list[str] | None = None) -> dict:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames or list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return {"file": ("upload.csv", out.getvalue().encode("utf-8"), "text/csv")}


def real_upload(path: str) -> dict:
    with open(path, "rb") as f:
        return {"file": ("data.csv", f.read(), "text/csv")}


# ============================== LGAs ==============================


def test_create_lga_records_verified_identity_and_is_public(client, db_session, make_token):
    response = client.post(
        "/api/admin/lgas", json=lga_body(), headers=headers(make_token, " Editor@Example.COM ")
    )

    assert response.status_code == 201
    body = response.json()
    assert body["slug"] == "test-lga"
    assert body["updated_by"] == "editor@example.com"
    assert body["updated_at"] and body["created_at"]
    public = client.get("/api/lgas").json()["lgas"]
    assert [lga["slug"] for lga in public] == ["test-lga"]
    assert public[0]["notablePlaces"] == ["A park", "A palace"]


def test_admin_list_includes_updated_by(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))

    [lga] = client.get("/api/admin/lgas", headers=headers(make_token)).json()

    assert (lga["slug"], lga["updated_by"]) == ("test-lga", "editor@example.com")
    # The public list never shows who edited it.
    assert "updatedBy" not in client.get("/api/lgas").json()["lgas"][0]


@pytest.mark.parametrize(
    ("overrides", "detail"),
    [
        ({"latitude": 95}, "invalid coordinates"),
        ({"longitude": -200}, "invalid coordinates"),
        ({"headquarters": "  "}, "missing required field(s): headquarters"),
        ({"lga_name": "///"}, "no letters or digits"),
    ],
)
def test_create_lga_uses_ingestion_validation(client, db_session, make_token, overrides, detail):
    response = client.post("/api/admin/lgas", json=lga_body(**overrides), headers=headers(make_token))

    assert response.status_code == 422
    assert detail in response.json()["detail"]
    assert db_session.query(Lga).count() == 0


def test_validation_errors_quote_numbers_as_typed(client, make_token):
    response = client.post("/api/admin/lgas", json=lga_body(latitude=200), headers=headers(make_token))
    assert "invalid coordinates '200', '5.2'" in response.json()["detail"]


def test_create_lga_requires_the_required_fields(client, db_session, make_token):
    body = lga_body()
    del body["verification_status"]
    assert client.post("/api/admin/lgas", json=body, headers=headers(make_token)).status_code == 422


def test_create_lga_rejects_a_duplicate_slug(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))
    # "Test-LGA" slugifies to the same "test-lga".
    response = client.post("/api/admin/lgas", json=lga_body(lga_name="Test-LGA"), headers=headers(make_token))

    assert response.status_code == 409
    assert db_session.query(Lga).count() == 1


@pytest.mark.parametrize(
    "spoof",
    [{"updated_by": "someone-else@example.com"}, {"updated_at": "2020-01-01T00:00:00"},
     {"slug": "chosen-slug"}, {"created_at": "2020-01-01T00:00:00"}],
)
def test_create_lga_cannot_set_system_fields(client, db_session, make_token, spoof):
    response = client.post("/api/admin/lgas", json=lga_body(**spoof), headers=headers(make_token))

    assert response.status_code == 422
    assert db_session.query(Lga).count() == 0


def test_edit_lga_changes_fields_and_restamps(client, db_session, make_token):
    created = client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token, "first@example.com")).json()

    response = client.patch(
        "/api/admin/lgas/test-lga",
        json={"headquarters": "New-Ekiti", "limitations": "Needs review"},
        headers=headers(make_token, "second@example.com"),
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["headquarters"], body["limitations"]) == ("New-Ekiti", "Needs review")
    # Untouched fields are kept.
    assert body["notable_places"] == "A park; A palace"
    assert body["updated_by"] == "second@example.com"
    assert body["updated_at"] >= created["updated_at"]
    assert client.get("/api/lgas").json()["lgas"][0]["headquarters"] == "New-Ekiti"


def test_edit_lga_that_changes_nothing_does_not_restamp(client, db_session, make_token):
    created = client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token, "first@example.com")).json()

    body = client.patch(
        "/api/admin/lgas/test-lga", json={"headquarters": "Test-Ekiti"},
        headers=headers(make_token, "second@example.com"),
    ).json()

    assert (body["updated_by"], body["updated_at"]) == ("first@example.com", created["updated_at"])


def test_edit_lga_can_clear_an_optional_field(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))
    body = client.patch("/api/admin/lgas/test-lga", json={"notable_places": None}, headers=headers(make_token)).json()
    assert body["notable_places"] is None


@pytest.mark.parametrize(
    ("patch", "status"),
    [
        ({"latitude": 200}, 422),
        ({"headquarters": None}, 422),
        ({"verification_status": ""}, 422),
        ({"updated_by": "someone-else@example.com"}, 422),
        ({"updated_at": "2020-01-01T00:00:00"}, 422),
        ({"slug": "other"}, 422),
    ],
)
def test_invalid_or_spoofed_lga_edit_changes_nothing(client, db_session, make_token, patch, status):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token, "first@example.com"))

    response = client.patch("/api/admin/lgas/test-lga", json=patch, headers=headers(make_token, "second@example.com"))

    assert response.status_code == status
    db_session.expire_all()
    lga = db_session.query(Lga).one()
    assert (lga.latitude, lga.headquarters, lga.verification_status, lga.updated_by) == (
        7.5, "Test-Ekiti", "Pending", "first@example.com"
    )


def test_renaming_an_lga_changes_its_slug(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))

    body = client.patch("/api/admin/lgas/test-lga", json={"lga_name": "Renamed LGA"}, headers=headers(make_token)).json()

    assert body["slug"] == "renamed-lga"
    assert client.patch("/api/admin/lgas/test-lga", json={}, headers=headers(make_token)).status_code == 404


def test_renaming_onto_an_existing_slug_is_refused(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))
    client.post("/api/admin/lgas", json=lga_body(lga_name="Other"), headers=headers(make_token))

    response = client.patch("/api/admin/lgas/other", json={"lga_name": "Test LGA"}, headers=headers(make_token))

    assert response.status_code == 409


def test_delete_lga_removes_it_everywhere(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token))

    response = client.delete("/api/admin/lgas/test-lga", headers=headers(make_token))

    assert response.status_code == 204
    assert client.get("/api/lgas").json() == {"lgas": []}
    assert client.get("/api/admin/lgas", headers=headers(make_token)).json() == []


@pytest.mark.parametrize(("method", "json"), [("patch", {"headquarters": "X"}), ("delete", None)])
def test_unknown_lga_is_404(client, make_token, method, json):
    response = client.request(method, "/api/admin/lgas/nowhere", json=json, headers=headers(make_token))
    assert response.status_code == 404


# ============================ Timeline ============================


def test_create_event_records_verified_identity_and_is_public(client, db_session, make_token):
    response = client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token))

    assert response.status_code == 201
    assert (response.json()["id"], response.json()["updated_by"]) == ("EK-900", "editor@example.com")
    [public] = client.get("/api/timeline").json()["events"]
    assert (public["id"], public["status"]) == ("EK-900", "Single source")


@pytest.mark.parametrize("status_value", ["Probably true", "verified", "VERIFIED", "", "Pending"])
def test_create_event_rejects_an_undocumented_verification_status(client, db_session, make_token, status_value):
    response = client.post(
        "/api/admin/timeline", json=event_body(verification_status=status_value), headers=headers(make_token)
    )

    assert response.status_code == 422
    assert db_session.query(TimelineEvent).count() == 0


@pytest.mark.parametrize("status_value", ["Verified", "Single source", "Needs primary source", "Conflicting sources"])
def test_create_event_accepts_each_documented_status(client, make_token, status_value):
    response = client.post(
        "/api/admin/timeline", json=event_body(verification_status=status_value), headers=headers(make_token)
    )
    assert response.status_code == 201


@pytest.mark.parametrize(
    ("overrides", "detail"),
    [
        ({"date_start": "January 2027"}, "invalid date_start"),
        ({"date_end": "2027-13"}, "invalid date_end"),
        ({"source": "none"}, "missing required field(s): source"),
    ],
)
def test_create_event_uses_ingestion_validation(client, db_session, make_token, overrides, detail):
    response = client.post("/api/admin/timeline", json=event_body(**overrides), headers=headers(make_token))

    assert response.status_code == 422
    assert detail in response.json()["detail"]
    assert db_session.query(TimelineEvent).count() == 0


def test_create_event_rejects_a_duplicate_id(client, db_session, make_token):
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token))
    response = client.post("/api/admin/timeline", json=event_body(event_title="Other"), headers=headers(make_token))
    assert response.status_code == 409


def test_edit_event_changes_fields_and_restamps(client, db_session, make_token):
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token, "first@example.com"))

    response = client.patch(
        "/api/admin/timeline/EK-900",
        json={"event_title": "Renamed", "date_display": "Early 2027"},
        headers=headers(make_token, "second@example.com"),
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["event_title"], body["date_display"], body["updated_by"]) == (
        "Renamed", "Early 2027", "second@example.com"
    )
    # Untouched by the edit.
    assert body["verification_status"] == "Single source"
    assert client.get("/api/timeline").json()["events"][0]["title"] == "Renamed"


@pytest.mark.parametrize(
    "patch",
    [
        {"verification_status": "Probably true"},
        {"verification_status": None},
        {"date_start": "sometime"},
        {"id": "EK-901"},
        {"updated_by": "someone-else@example.com"},
        {"updated_at": "2020-01-01T00:00:00"},
    ],
)
def test_invalid_or_spoofed_event_edit_changes_nothing(client, db_session, make_token, patch):
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token, "first@example.com"))

    response = client.patch("/api/admin/timeline/EK-900", json=patch, headers=headers(make_token, "second@example.com"))

    assert response.status_code == 422
    db_session.expire_all()
    event = db_session.get(TimelineEvent, "EK-900")
    assert (event.verification_status, event.date_start, event.updated_by) == (
        "Single source", "2027-01", "first@example.com"
    )


def test_delete_event_removes_it_everywhere(client, db_session, make_token):
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token))

    assert client.delete("/api/admin/timeline/EK-900", headers=headers(make_token)).status_code == 204
    assert client.get("/api/timeline").json() == {"events": []}


@pytest.mark.parametrize(("method", "json"), [("patch", {"event_title": "X"}), ("delete", None)])
def test_unknown_event_is_404(client, make_token, method, json):
    response = client.request(method, "/api/admin/timeline/EK-999", json=json, headers=headers(make_token))
    assert response.status_code == 404


# ============================ CSV import ============================

IMPORTS = {
    # kind: (import URL, real CSV, model, key attribute on SkippedRow, service)
    "lgas": ("/api/admin/lgas/import", LGA_CSV, Lga, "lga_name", lga_ingestion),
    "timeline": ("/api/admin/timeline/import", TIMELINE_CSV, TimelineEvent, "event_id", timeline_ingestion),
}
REAL_COUNTS = {"lgas": 16, "timeline": 50}


@pytest.fixture(params=list(IMPORTS))
def kind(request):
    return request.param


def test_import_real_csv_creates_every_row_with_importer_identity(client, db_session, make_token, kind):
    url, path, model, _, _ = IMPORTS[kind]

    response = client.post(url, files=real_upload(path), headers=headers(make_token, "importer@example.com"))

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert (len(body["created"]), body["updated"], body["unchanged"], body["skipped"]) == (
        REAL_COUNTS[kind], [], [], []
    )
    rows = db_session.query(model).all()
    assert len(rows) == REAL_COUNTS[kind]
    assert {row.updated_by for row in rows} == {"importer@example.com"}
    assert all(row.updated_at is not None for row in rows)


def test_import_preview_writes_nothing_and_matches_the_real_import(client, db_session, make_token, kind):
    url, path, model, _, _ = IMPORTS[kind]

    preview = client.post(f"{url}?dry_run=true", files=real_upload(path), headers=headers(make_token)).json()

    assert preview["dry_run"] is True
    assert len(preview["created"]) == REAL_COUNTS[kind]
    assert db_session.query(model).count() == 0

    real = client.post(url, files=real_upload(path), headers=headers(make_token)).json()
    assert {k: v for k, v in real.items() if k != "dry_run"} == {k: v for k, v in preview.items() if k != "dry_run"}


def test_reimporting_the_same_csv_changes_nothing(client, db_session, make_token, kind):
    url, path, model, _, _ = IMPORTS[kind]
    client.post(url, files=real_upload(path), headers=headers(make_token, "first@example.com"))

    body = client.post(url, files=real_upload(path), headers=headers(make_token, "second@example.com")).json()

    assert (body["created"], body["updated"], len(body["unchanged"])) == ([], [], REAL_COUNTS[kind])
    # Not re-stamped: the second admin didn't change anything.
    assert {row.updated_by for row in db_session.query(model)} == {"first@example.com"}


def test_import_updates_only_rows_that_changed(client, db_session, make_token, kind):
    url, path, model, _, service = IMPORTS[kind]
    client.post(url, files=real_upload(path), headers=headers(make_token, "first@example.com"))
    rows = service.read_csv(path)
    key_field, edit_field = ("lga_name", "limitations") if kind == "lgas" else ("id", "notes_limitations")
    rows[3][edit_field] = "Corrected in an import"

    body = client.post(url, files=csv_upload(rows), headers=headers(make_token, "second@example.com")).json()

    expected_key = lga_ingestion.slugify(rows[3][key_field]) if kind == "lgas" else rows[3][key_field]
    assert body["updated"] == [expected_key]
    assert len(body["unchanged"]) == REAL_COUNTS[kind] - 1
    stamps = {row.updated_by for row in db_session.query(model)}
    assert stamps == {"first@example.com", "second@example.com"}


def test_import_skips_bad_rows_with_the_same_reasons_as_the_cli(client, db_session, make_token, kind):
    url, path, model, key_attr, service = IMPORTS[kind]
    rows = service.read_csv(path)[:5]
    if kind == "lgas":
        rows[1]["latitude"] = "north"
        rows[3]["headquarters"] = ""
    else:
        rows[1]["verification_status"] = "Probably true"
        rows[3]["date_start"] = "sometime"

    body = client.post(url, files=csv_upload(rows), headers=headers(make_token)).json()

    _, cli_skipped = service.validate_rows(rows)
    assert body["skipped"] == [
        {"line": s.line, "key": getattr(s, key_attr), "reason": s.reason} for s in cli_skipped
    ]
    assert [s["line"] for s in body["skipped"]] == [3, 5]
    assert len(body["created"]) == 3
    assert db_session.query(model).count() == 3


def test_import_rejects_the_wrong_file(client, db_session, make_token):
    # The timeline CSV sent to the LGA import has none of the LGA columns.
    response = client.post("/api/admin/lgas/import", files=real_upload(TIMELINE_CSV), headers=headers(make_token))

    assert response.status_code == 422
    assert "missing required column(s)" in response.json()["detail"]
    assert db_session.query(Lga).count() == 0


@pytest.mark.parametrize(
    ("content", "status", "detail"),
    [
        ("lga_name,headquarters\n".encode(), 422, "no data rows"),
        (b"", 422, "no data rows"),
        ("lga_name\nÀdó\n".encode("utf-16"), 422, "UTF-8"),
    ],
)
def test_import_rejects_unusable_files(client, make_token, content, status, detail):
    response = client.post(
        "/api/admin/lgas/import", files={"file": ("x.csv", content, "text/csv")}, headers=headers(make_token)
    )
    assert response.status_code == status
    assert detail in response.json()["detail"]


def test_import_rejects_an_oversized_file(client, make_token, monkeypatch):
    from app.api.routes import content_admin

    monkeypatch.setattr(content_admin, "MAX_IMPORT_BYTES", 100)
    response = client.post("/api/admin/lgas/import", files=real_upload(LGA_CSV), headers=headers(make_token))
    assert response.status_code == 413


def test_import_accepts_a_byte_order_mark(client, db_session, make_token):
    with open(LGA_CSV, "rb") as f:
        data = b"\xef\xbb\xbf" + f.read()
    response = client.post(
        "/api/admin/lgas/import", files={"file": ("bom.csv", data, "text/csv")}, headers=headers(make_token)
    )
    assert len(response.json()["created"]) == 16


def test_admin_import_overwrites_other_admins_edits_and_says_so(client, db_session, make_token):
    # The admin import is the research team's channel: it isn't held back by
    # earlier admin edits, but the result still lists which it overwrote.
    client.post("/api/admin/lgas/import", files=real_upload(LGA_CSV), headers=headers(make_token, "admin1@example.com"))
    client.patch("/api/admin/lgas/moba", json={"limitations": "Edited in the admin UI"}, headers=headers(make_token))

    body = client.post("/api/admin/lgas/import", files=real_upload(LGA_CSV), headers=headers(make_token, "admin2@example.com")).json()

    assert body["updated"] == ["moba"]
    db_session.expire_all()
    assert db_session.query(Lga).filter_by(slug="moba").one().updated_by == "admin2@example.com"


# ===================== verification_status is locked on edit =====================


@pytest.mark.parametrize("status_value", ["Verified", "Pending", "Pending review"])
def test_lga_edit_cannot_change_verification_status(client, db_session, make_token, status_value):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token, "first@example.com"))

    response = client.patch(
        "/api/admin/lgas/test-lga",
        json={"verification_status": status_value, "headquarters": "Changed-Ekiti"},
        headers=headers(make_token, "second@example.com"),
    )

    assert response.status_code == 422
    db_session.expire_all()
    lga = db_session.query(Lga).one()
    # The whole edit is refused, including the fields that were allowed.
    assert (lga.verification_status, lga.headquarters, lga.updated_by) == ("Pending", "Test-Ekiti", "first@example.com")


@pytest.mark.parametrize("status_value", ["Verified", "Single source", "Needs primary source", "Conflicting sources"])
def test_event_edit_cannot_change_verification_status(client, db_session, make_token, status_value):
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token, "first@example.com"))

    response = client.patch(
        "/api/admin/timeline/EK-900", json={"verification_status": status_value}, headers=headers(make_token)
    )

    assert response.status_code == 422
    db_session.expire_all()
    assert db_session.get(TimelineEvent, "EK-900").verification_status == "Single source"


def test_create_can_set_verification_status(client, make_token):
    lga = client.post("/api/admin/lgas", json=lga_body(verification_status="Verified"), headers=headers(make_token))
    event = client.post("/api/admin/timeline", json=event_body(verification_status="Verified"), headers=headers(make_token))

    assert (lga.status_code, lga.json()["verification_status"]) == (201, "Verified")
    assert (event.status_code, event.json()["verification_status"]) == (201, "Verified")


def test_import_can_change_verification_status(client, db_session, make_token, kind):
    url, path, model, _, service = IMPORTS[kind]
    client.post(url, files=real_upload(path), headers=headers(make_token))
    rows = service.read_csv(path)
    old = rows[0]["verification_status"]
    new = "Verified" if kind == "lgas" else ("Single source" if old == "Verified" else "Verified")
    rows[0]["verification_status"] = new

    body = client.post(url, files=csv_upload(rows), headers=headers(make_token, "research@example.com")).json()

    assert len(body["updated"]) == 1
    db_session.expire_all()
    key = body["updated"][0]
    row = db_session.query(model).filter_by(**({"slug": key} if kind == "lgas" else {"id": key})).one()
    assert (row.verification_status, row.updated_by) == (new, "research@example.com")


# ============================ Access ============================

ADMIN_CALLS = [
    ("get", "/api/admin/lgas", None, None),
    ("post", "/api/admin/lgas", lga_body(), None),
    ("patch", "/api/admin/lgas/test-lga", {"headquarters": "X"}, None),
    ("delete", "/api/admin/lgas/test-lga", None, None),
    ("post", "/api/admin/lgas/import", None, LGA_CSV),
    ("get", "/api/admin/timeline", None, None),
    ("post", "/api/admin/timeline", event_body(id="EK-901"), None),
    ("patch", "/api/admin/timeline/EK-900", {"event_title": "X"}, None),
    ("delete", "/api/admin/timeline/EK-900", None, None),
    ("post", "/api/admin/timeline/import", None, TIMELINE_CSV),
]


@pytest.fixture
def seeded(client, db_session, make_token):
    client.post("/api/admin/lgas", json=lga_body(), headers=headers(make_token, "owner@example.com"))
    client.post("/api/admin/timeline", json=event_body(), headers=headers(make_token, "owner@example.com"))


def _snapshot(db_session):
    db_session.expire_all()
    return (
        [(l.slug, l.headquarters, l.updated_by) for l in db_session.query(Lga).order_by(Lga.slug)],
        [(e.id, e.event_title, e.updated_by) for e in db_session.query(TimelineEvent).order_by(TimelineEvent.id)],
    )


@pytest.mark.parametrize(("method", "url", "json", "upload"), ADMIN_CALLS)
@pytest.mark.parametrize(
    ("who", "expected"),
    [("nobody", 401), ("contributor", 403), ("forged", 401)],
)
def test_non_admins_cannot_reach_any_admin_content_endpoint(
    client, db_session, make_token, seeded, method, url, json, upload, who, expected
):
    before = _snapshot(db_session)
    auth = {
        "nobody": {},
        "contributor": headers(make_token, "c@example.com", role="contributor"),
        "forged": {"Authorization": "Bearer " + make_token(secret="a-different-secret-that-is-long-enough")},
    }[who]

    response = client.request(
        method, url, json=json, files=real_upload(upload) if upload else None, headers=auth
    )

    assert response.status_code == expected
    assert _snapshot(db_session) == before
