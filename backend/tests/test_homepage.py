"""Homepage content: the migration, admin CRUD/reorder/images, the public feed, the seed."""

import importlib.util
from pathlib import Path

import httpx
import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect

from app.models.base import Base
from app.models.homepage import HeroContent, HeroImage, Landmark, Leader, Moment
from app.services import cloudinary_upload, homepage_seed

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

HOMEPAGE_TABLES = {
    "homepage_hero",
    "homepage_hero_images",
    "homepage_leaders",
    "homepage_landmarks",
    "homepage_moments",
}
MIGRATION = Path(__file__).parents[1] / "alembic" / "versions" / "6fbd4fdce746_create_homepage_content_tables.py"

LISTS = {
    "leaders": {"name": "Ada Ekiti", "term": "2030–2034"},
    "landmarks": {"name": "Efon Alaaye Hills", "description": "Efon-Alaaye", "placeholder_icon": "hill"},
    "moments": {"year": "2030", "label": "A new chapter", "is_anchor": False, "placeholder_icon": "book"},
    "hero/images": {"caption": "Ado-Ekiti market", "placeholder_icon": "pin"},
}


def headers(make_token, email="editor@example.com", role="admin"):
    return {"Authorization": f"Bearer {make_token(role=role, email=email)}"}


@pytest.fixture
def seeded(db_session):
    homepage_seed.seed(db_session, updated_by="cli:test")
    return db_session


class FakeCloudinary:
    def __init__(self):
        self.calls = []

    def post(self, url, data=None, files=None, timeout=None):
        self.calls.append({"folder": data["folder"], "filename": files["file"][0]})
        return httpx.Response(
            200,
            json={"secure_url": f"https://res.cloudinary.com/ekiti-test/image/upload/v1/{data['folder']}/x.png", "format": "png"},
            request=httpx.Request("POST", url),
        )


@pytest.fixture
def cloudinary(monkeypatch):
    fake = FakeCloudinary()
    monkeypatch.setattr(cloudinary_upload.httpx, "post", fake.post)
    return fake


# --- Migration -------------------------------------------------------------


def _load_migration():
    spec = importlib.util.spec_from_file_location("homepage_migration", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_creates_exactly_the_model_tables_and_drops_them_again():
    # The earlier revisions need Postgres (pgvector), so run just this one on
    # SQLite; the full chain was run on Postgres (upgrade/downgrade/check).
    migration = _load_migration()
    assert migration.down_revision == "deb598b23c08"
    engine = create_engine("sqlite://")
    homepage_metadata = Base.metadata
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            migration.upgrade()
        assert set(inspect(conn).get_table_names()) == HOMEPAGE_TABLES
        diff = [
            d for d in compare_metadata(ctx, homepage_metadata)
            if not (d[0] == "add_table" and d[1].name not in HOMEPAGE_TABLES)
            and not (d[0] == "add_index" and d[1].table.name not in HOMEPAGE_TABLES)
        ]
        assert diff == []
        with Operations.context(ctx):
            migration.downgrade()
        assert inspect(conn).get_table_names() == []


def test_models_record_timestamps_and_default_updated_by(db_session):
    leader = Leader(name="A", term="1", position=0)
    db_session.add(leader)
    db_session.commit()
    assert leader.created_at is not None and leader.updated_at is not None
    assert leader.updated_by is None
    moment = Moment(year="1", label="x", position=0, placeholder_icon="star")
    db_session.add(moment)
    db_session.commit()
    assert moment.is_anchor is False


# --- Auth ------------------------------------------------------------------


ADMIN_REQUESTS = [
    ("get", "/api/admin/homepage/hero", None),
    ("patch", "/api/admin/homepage/hero", {"eyebrow": "x"}),
    *[
        request
        for path, body in LISTS.items()
        for request in (
            ("get", f"/api/admin/homepage/{path}", None),
            ("post", f"/api/admin/homepage/{path}", body),
            ("patch", f"/api/admin/homepage/{path}/1", {}),
            ("delete", f"/api/admin/homepage/{path}/1", None),
            ("post", f"/api/admin/homepage/{path}/reorder", {"ids": [1]}),
            ("delete", f"/api/admin/homepage/{path}/1/image", None),
        )
    ],
]


@pytest.mark.parametrize("method,path,body", ADMIN_REQUESTS, ids=[f"{m} {p}" for m, p, _ in ADMIN_REQUESTS])
def test_non_admins_get_403_and_anonymous_401(client, seeded, contributor_headers, method, path, body):
    kwargs = {"json": body} if body is not None else {}
    assert getattr(client, method)(path, headers=contributor_headers, **kwargs).status_code == 403
    assert getattr(client, method)(path, **kwargs).status_code == 401


@pytest.mark.parametrize("path", list(LISTS))
def test_non_admin_image_upload_is_403_and_never_reaches_cloudinary(client, seeded, contributor_headers, cloudinary, path):
    response = client.post(
        f"/api/admin/homepage/{path}/1/image", files={"file": ("a.png", PNG, "image/png")}, headers=contributor_headers
    )
    assert response.status_code == 403
    assert cloudinary.calls == []


def test_non_admin_changes_nothing(client, seeded, contributor_headers):
    client.patch("/api/admin/homepage/leaders/1", json={"name": "Hacked"}, headers=contributor_headers)
    client.delete("/api/admin/homepage/leaders/2", headers=contributor_headers)
    names = [leader["name"] for leader in client.get("/api/homepage").json()["leaders"]]
    assert names == [row["name"] for row in homepage_seed.LEADERS]


# --- List CRUD -------------------------------------------------------------


@pytest.mark.parametrize("path", list(LISTS))
def test_create_appends_at_the_end_with_the_admins_identity(client, seeded, make_token, path):
    before = client.get(f"/api/admin/homepage/{path}", headers=headers(make_token)).json()
    if path == "hero/images":
        client.delete(f"/api/admin/homepage/{path}/{before[-1]['id']}", headers=headers(make_token))
        before = before[:-1]
    response = client.post(f"/api/admin/homepage/{path}", json=LISTS[path], headers=headers(make_token, "Editor@Example.com "))
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["position"] == len(before)
    assert created["updated_by"] == "editor@example.com"
    assert created["image_url"] is None
    after = client.get(f"/api/admin/homepage/{path}", headers=headers(make_token)).json()
    assert [i["id"] for i in after] == [i["id"] for i in before] + [created["id"]]


@pytest.mark.parametrize(
    "path,field",
    [("leaders", "name"), ("landmarks", "name"), ("moments", "label"), ("hero/images", "caption")],
)
def test_patch_edits_one_field_and_records_who(client, seeded, make_token, path, field):
    response = client.patch(f"/api/admin/homepage/{path}/2", json={field: "  Edited  "}, headers=headers(make_token, "b@example.com"))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body[field] == "Edited"
    assert body["updated_by"] == "b@example.com"


@pytest.mark.parametrize(
    "body",
    [
        {"updated_by": "someone@else.com"},
        {"updated_at": "2020-01-01T00:00:00"},
        {"image_url": "https://evil.example/x.png"},
        {"position": 9},
        {"id": 5},
        {"name": None},
        {"name": "   "},
    ],
    ids=["updated_by", "updated_at", "image_url", "position", "id", "null", "blank"],
)
def test_patch_rejects_server_owned_and_empty_fields(client, seeded, make_token, body):
    response = client.patch("/api/admin/homepage/leaders/1", json=body, headers=headers(make_token))
    assert response.status_code == 422
    assert client.get("/api/admin/homepage/leaders", headers=headers(make_token)).json()[0]["updated_by"] == "cli:test"


def test_create_rejects_an_unknown_placeholder_icon(client, seeded, make_token):
    body = {**LISTS["landmarks"], "placeholder_icon": "rocket"}
    assert client.post("/api/admin/homepage/landmarks", json=body, headers=headers(make_token)).status_code == 422


def test_missing_items_are_404(client, seeded, make_token):
    h = headers(make_token)
    assert client.patch("/api/admin/homepage/moments/999", json={"year": "1"}, headers=h).status_code == 404
    assert client.delete("/api/admin/homepage/moments/999", headers=h).status_code == 404
    assert client.delete("/api/admin/homepage/moments/999/image", headers=h).status_code == 404


def test_delete_removes_the_item_and_closes_the_gap(client, seeded, make_token):
    h = headers(make_token)
    assert client.delete("/api/admin/homepage/leaders/3", headers=h).status_code == 204
    leaders = client.get("/api/admin/homepage/leaders", headers=h).json()
    assert [leader["id"] for leader in leaders] == [1, 2, 4, 5, 6, 7]
    assert [leader["position"] for leader in leaders] == [0, 1, 2, 3, 4, 5]


def test_hero_images_are_capped_at_three(client, seeded, make_token):
    response = client.post("/api/admin/homepage/hero/images", json=LISTS["hero/images"], headers=headers(make_token))
    assert response.status_code == 409
    assert seeded.query(HeroImage).count() == 3


# --- Reorder ---------------------------------------------------------------


def test_reorder_sets_the_new_order_everywhere(client, seeded, make_token):
    h = headers(make_token, "r@example.com")
    response = client.post("/api/admin/homepage/moments/reorder", json={"ids": [5, 1, 2, 3, 4]}, headers=h)
    assert response.status_code == 200, response.text
    assert [m["id"] for m in response.json()] == [5, 1, 2, 3, 4]
    assert [m["year"] for m in client.get("/api/homepage").json()["moments"]] == ["2026", "1996", "1999", "2010s", "2022"]
    # Every row moved, so every row records who moved it.
    assert {m["updated_by"] for m in response.json()} == {"r@example.com"}


def test_reorder_touches_only_rows_that_moved(client, seeded, make_token):
    response = client.post("/api/admin/homepage/leaders/reorder", json={"ids": [2, 1, 3, 4, 5, 6, 7]}, headers=headers(make_token, "r@example.com"))
    by_id = {leader["id"]: leader["updated_by"] for leader in response.json()}
    assert by_id[1] == by_id[2] == "r@example.com"
    assert {by_id[i] for i in range(3, 8)} == {"cli:test"}


@pytest.mark.parametrize(
    "ids",
    [[1, 2, 3], [1, 2, 3, 4, 5, 6, 7, 8], [1, 1, 2, 3, 4, 5, 6], [7, 6, 5, 4, 3, 2, 99]],
    ids=["missing", "unknown", "duplicate", "swapped-for-unknown"],
)
def test_reorder_must_list_every_id_exactly_once(client, seeded, make_token, ids):
    response = client.post("/api/admin/homepage/leaders/reorder", json={"ids": ids}, headers=headers(make_token))
    assert response.status_code == 422
    assert [leader["id"] for leader in client.get("/api/homepage").json()["leaders"]] == [1, 2, 3, 4, 5, 6, 7]


# --- Images ----------------------------------------------------------------


@pytest.mark.parametrize(
    "path,folder",
    [
        ("leaders", "EKITI30/Homepage/Leaders"),
        ("landmarks", "EKITI30/Homepage/Landmarks"),
        ("moments", "EKITI30/Homepage/Moments"),
        ("hero/images", "EKITI30/Homepage/Hero"),
    ],
)
def test_image_upload_goes_to_the_sections_folder(client, seeded, make_token, cloudinary, path, folder):
    response = client.post(
        f"/api/admin/homepage/{path}/1/image", files={"file": ("photo.png", PNG, "image/png")}, headers=headers(make_token, "i@example.com")
    )
    assert response.status_code == 200, response.text
    assert cloudinary.calls == [{"folder": folder, "filename": "photo.png"}]
    assert response.json()["image_url"].startswith(f"https://res.cloudinary.com/ekiti-test/image/upload/v1/{folder}/")
    assert response.json()["updated_by"] == "i@example.com"

    cleared = client.delete(f"/api/admin/homepage/{path}/1/image", headers=headers(make_token))
    assert cleared.status_code == 200
    assert cleared.json()["image_url"] is None


def test_a_non_image_is_rejected_before_cloudinary(client, seeded, make_token, cloudinary):
    response = client.post(
        "/api/admin/homepage/leaders/1/image", files={"file": ("notes.png", b"hello", "image/png")}, headers=headers(make_token)
    )
    assert response.status_code == 422
    assert cloudinary.calls == []
    assert seeded.get(Leader, 1).image_url is None


def test_homepage_folders_are_admin_only():
    from app.services.cloudinary_convention import ADMIN_ONLY_FOLDERS, ALLOWED_FOLDERS, validate_admin_folder, validate_folder

    for folder in ADMIN_ONLY_FOLDERS:
        assert folder.startswith("EKITI30/Homepage/")
        # Member uploads (/api/uploads/init) can't target them...
        assert not validate_folder(folder)
        # ...but admin uploads can, as well as every member folder.
        assert validate_admin_folder(folder)
    assert all(validate_admin_folder(f) for f in ALLOWED_FOLDERS)


# --- Hero ------------------------------------------------------------------


def test_hero_get_and_patch(client, seeded, make_token):
    h = headers(make_token, "h@example.com")
    assert client.get("/api/admin/homepage/hero", headers=h).json()["eyebrow"] == homepage_seed.HERO["eyebrow"]
    response = client.patch("/api/admin/homepage/hero", json={"headline": "Hello.\nIt's *us*."}, headers=h)
    assert response.status_code == 200, response.text
    assert response.json()["headline"] == "Hello.\nIt's *us*."
    assert response.json()["subtitle"] == homepage_seed.HERO["subtitle"]
    assert response.json()["updated_by"] == "h@example.com"


def test_hero_404_until_set_up_and_first_save_needs_every_field(client, make_token):
    h = headers(make_token)
    assert client.get("/api/admin/homepage/hero", headers=h).status_code == 404
    assert client.patch("/api/admin/homepage/hero", json={"eyebrow": "x"}, headers=h).status_code == 422
    assert client.patch("/api/admin/homepage/hero", json=homepage_seed.HERO, headers=h).status_code == 200
    assert client.get("/api/homepage").json()["hero"]["eyebrow"] == homepage_seed.HERO["eyebrow"]


@pytest.mark.parametrize(
    "body",
    [
        {"headline": "Welcome <b>home</b>"},
        {"headline": "<script>alert(1)</script>"},
        {"headline": "Thirty years of *us."},
        {"headline": "Empty ** emphasis"},
        {"primary_cta_href": "javascript:alert(1)"},
        {"secondary_cta_href": "//evil.example"},
        {"secondary_cta_href": "http://insecure.example"},
        {"facts": []},
        {"facts": [{"label": "a", "value": "b"}] * 7},
        {"facts": [{"label": "a"}]},
    ],
    ids=["html", "script", "unclosed-em", "empty-em", "js-href", "protocol-relative", "http", "no-facts", "too-many-facts", "fact-no-value"],
)
def test_hero_rejects_markup_unsafe_links_and_bad_facts(client, seeded, make_token, body):
    assert client.patch("/api/admin/homepage/hero", json=body, headers=headers(make_token)).status_code == 422
    assert seeded.get(HeroContent, 1).updated_by == "cli:test"


# --- Public feed -----------------------------------------------------------


def test_public_homepage_is_empty_before_seeding(client):
    assert client.get("/api/homepage").json() == {"hero": None, "leaders": [], "landmarks": [], "moments": []}


def test_public_homepage_is_ordered_by_position_then_id(client, db_session):
    db_session.add_all([
        Leader(name="Third", term="t", position=2),
        Leader(name="First", term="t", position=0),
        Leader(name="Second (tie, lower id)", term="t", position=1),
        Leader(name="Second (tie, higher id)", term="t", position=1),
    ])
    db_session.commit()
    names = [leader["name"] for leader in client.get("/api/homepage").json()["leaders"]]
    assert names == ["First", "Second (tie, lower id)", "Second (tie, higher id)", "Third"]


def test_public_homepage_is_camelcase_and_leaves_out_admin_fields(client, seeded):
    body = client.get("/api/homepage").json()
    assert set(body["hero"]) == {"eyebrow", "headline", "subtitle", "primaryCta", "secondaryCta", "facts", "images"}
    assert set(body["hero"]["images"][0]) == {"id", "caption", "imageUrl", "placeholderIcon"}
    assert set(body["leaders"][0]) == {"id", "name", "term", "imageUrl"}
    assert set(body["landmarks"][0]) == {"id", "name", "description", "imageUrl", "placeholderIcon"}
    assert set(body["moments"][0]) == {"id", "year", "label", "isAnchor", "imageUrl", "placeholderIcon"}


# --- Seed ------------------------------------------------------------------


def test_seed_produces_the_original_homepage(client, seeded):
    body = client.get("/api/homepage").json()
    hero = body["hero"]
    assert hero["eyebrow"] == "Marking 30 years of Ekiti State, 1996–2026"
    assert hero["headline"] == "Welcome home.\nThirty years of *us*."
    assert hero["subtitle"] == (
        "The leaders who guided us, the hills and springs that raised us, the moments we celebrated "
        "together — one place to remember where we've been, and imagine where we're going."
    )
    assert hero["primaryCta"] == {"label": "Walk Through Our Journey", "href": "#moments"}
    assert hero["secondaryCta"] == {"label": "Share Your Ekiti Story", "href": "/my-ekiti-story"}
    assert [(f["label"], f["value"]) for f in hero["facts"]] == [
        ("Created", "1 Oct 1996"), ("Local governments", "16"), ("Capital", "Ado-Ekiti"), ("Leaders since", "7"),
    ]
    assert [(i["caption"], i["placeholderIcon"]) for i in hero["images"]] == [
        ("Fajuyi Park, Ado-Ekiti", "document"), ("Governors, 1996–2026", "person"), ("Ikogosi Warm Springs", "springs"),
    ]
    assert [(leader["name"], leader["term"]) for leader in body["leaders"]] == [
        ("Mohammed Bawa", "1996–1998"),
        ("Atanda Yusuf", "1998–1999"),
        ("Niyi Adebayo", "1999–2003"),
        ("Ayodele Fayose", "2003–2006, 2014–2018"),
        ("Segun Oni", "2007–2010"),
        ("Kayode Fayemi", "2010–2014, 2018–2022"),
        ("Biodun Oyebanji", "2022–present"),
    ]
    assert [(la["name"], la["description"], la["placeholderIcon"]) for la in body["landmarks"]] == [
        ("Ikogosi Warm Springs", "Ikogosi-Ekiti · where warm and cold waters meet", "springs"),
        ("Arinta Waterfalls", "Ipole-Iloro, Ekiti West", "waterfall"),
        ("Fajuyi Memorial Park", "Ado-Ekiti, the state capital", "document"),
        ("Olosunta Hill", "Ikere-Ekiti · sacred hill and skyline", "hill"),
    ]
    assert [(m["year"], m["label"], m["isAnchor"], m["placeholderIcon"]) for m in body["moments"]] == [
        ("1996", "Ekiti State is created from Ondo State", True, "star"),
        ("1999", "First elected civilian governor takes office", False, "house"),
        ("2010s", "Growth in roads, schools and healthcare access", False, "book"),
        ("2022", "A new administration continues the journey", False, "pin"),
        ("2026", "Ekiti turns 30 — and we're building this, together", True, "celebration"),
    ]
    # No images yet: every card shows its placeholder.
    assert all(item["imageUrl"] is None for section in ("leaders", "landmarks", "moments") for item in body[section])


def test_seed_records_the_cli_identity(seeded):
    for model in (HeroContent, HeroImage, Leader, Landmark, Moment):
        assert {row.updated_by for row in seeded.query(model)} == {"cli:test"}


def test_seed_again_keeps_admin_edits(client, seeded, make_token):
    client.patch("/api/admin/homepage/leaders/1", json={"name": "Edited"}, headers=headers(make_token))
    client.delete("/api/admin/homepage/moments/5", headers=headers(make_token))
    result = homepage_seed.seed(seeded, updated_by="cli:again")
    assert result.seeded == []
    assert result.kept == ["hero", "hero images", "leaders", "landmarks", "moments"]
    body = client.get("/api/homepage").json()
    assert body["leaders"][0]["name"] == "Edited"
    assert len(body["moments"]) == 4


def test_seed_fills_only_empty_sections(db_session):
    db_session.add(Leader(name="Already here", term="x", position=0))
    db_session.commit()
    result = homepage_seed.seed(db_session, updated_by="cli:test")
    assert "leaders" in result.kept and "moments" in result.seeded
    assert [leader.name for leader in db_session.query(Leader)] == ["Already here"]
