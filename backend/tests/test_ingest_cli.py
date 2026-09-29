"""The CLI ingestion scripts (scripts/ingest_lgas.py, scripts/ingest_timeline.py).

Run for real against a temporary SQLite file: attribution, the admin-edit
warning, and --force.
"""

import getpass
import importlib.util
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.base import Base
from app.models.lga import Lga
from app.models.timeline_event import TimelineEvent
from app.services.attribution import cli_identity, is_admin_attribution

SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "scripts")

KINDS = {
    # kind: (script, model, a key in the real CSV, filter for that key, a field to edit)
    "lgas": ("ingest_lgas.py", Lga, "moba", "slug", "limitations"),
    "timeline": ("ingest_timeline.py", TimelineEvent, "EK-001", "id", "notes_limitations"),
}


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), os.path.join(SCRIPTS, name))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "cli.db"
    url = f"sqlite:///{path.as_posix()}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setattr(getpass, "getuser", lambda: "ayo")
    yield engine
    engine.dispose()


@pytest.fixture(params=list(KINDS))
def kind(request):
    return request.param


def run(kind: str, *args: str) -> int:
    return load_script(KINDS[kind][0]).main(list(args))


def row(engine, kind: str):
    _, model, key, key_field, _ = KINDS[kind]
    with Session(engine) as session:
        return session.query(model).filter_by(**{key_field: key}).one()


def admin_edit(engine, kind: str, email: str = "editor@example.com") -> None:
    """Simulate an edit made in the admin UI."""
    _, model, key, key_field, field = KINDS[kind]
    with Session(engine) as session:
        record = session.query(model).filter_by(**{key_field: key}).one()
        setattr(record, field, "Corrected in the admin UI")
        record.updated_by = email
        session.commit()


# --- Identity ---


@pytest.mark.parametrize(
    ("username", "expected"),
    [("ayo", "cli:ayo"), ("Ayobami Ogunlade", "cli:Ayobami-Ogunlade"), ("me@example.com", "cli:me-example.com"),
     ("", "cli:unknown"), ("../..", "cli:unknown")],
)
def test_cli_identity_can_never_look_like_an_email(username, expected):
    identity = cli_identity(username)
    assert identity == expected
    assert "@" not in identity
    assert not is_admin_attribution(identity)


@pytest.mark.parametrize(
    ("value", "is_admin"),
    [("editor@example.com", True), ("cli:ayo", False), (None, False), ("", False)],
)
def test_is_admin_attribution(value, is_admin):
    assert is_admin_attribution(value) is is_admin


# --- Scripts ---


def test_cli_records_its_own_identity_never_none(database, kind, capsys):
    assert run(kind) == 0

    out = capsys.readouterr().out
    assert "updated_by = 'cli:ayo'" in out
    _, model, *_ = KINDS[kind]
    with Session(database) as session:
        assert {r.updated_by for r in session.query(model)} == {"cli:ayo"}


def test_cli_holds_back_rows_an_admin_edited_without_force(database, kind, capsys):
    run(kind)
    admin_edit(database, kind)
    capsys.readouterr()

    status = run(kind)

    out = capsys.readouterr().out
    key = KINDS[kind][2]
    assert status == 1
    assert "WARNING: this CSV would overwrite 1 row(s) last changed by an admin" in out
    assert f"{key}  (last changed by editor@example.com)" in out
    assert "Without --force these rows are skipped" in out
    assert "Held back: 1" in out
    assert f"{key}: last changed by editor@example.com" in out
    # The admin's edit and attribution survive.
    record = row(database, kind)
    assert getattr(record, KINDS[kind][4]) == "Corrected in the admin UI"
    assert record.updated_by == "editor@example.com"


def test_cli_still_imports_every_other_row_without_force(database, kind, capsys):
    run(kind)
    admin_edit(database, kind)
    # Change a different row in the database so the CSV has something to fix.
    _, model, key, key_field, field = KINDS[kind]
    with Session(database) as session:
        other = session.query(model).filter(getattr(model, key_field) != key).first()
        other_key = getattr(other, key_field)
        setattr(other, field, "Drifted")
        other.updated_by = "cli:someone-else"
        session.commit()
    capsys.readouterr()

    run(kind)

    out = capsys.readouterr().out
    assert "Updated: 1" in out
    with Session(database) as session:
        fixed = session.query(model).filter_by(**{key_field: other_key}).one()
        assert getattr(fixed, field) != "Drifted"
        assert fixed.updated_by == "cli:ayo"


def test_cli_force_overwrites_admin_edits_after_warning(database, kind, capsys):
    run(kind)
    admin_edit(database, kind)
    capsys.readouterr()

    status = run(kind, "--force")

    out = capsys.readouterr().out
    assert status == 0
    assert "WARNING: this CSV would overwrite 1 row(s)" in out
    assert "--force given: these rows WILL be overwritten" in out
    assert "Held back: 0" in out
    record = row(database, kind)
    assert getattr(record, KINDS[kind][4]) != "Corrected in the admin UI"
    assert record.updated_by == "cli:ayo"


def test_cli_does_not_warn_about_rows_the_cli_last_changed(database, kind, capsys):
    run(kind)
    capsys.readouterr()

    assert run(kind) == 0
    assert "WARNING" not in capsys.readouterr().out


def test_cli_dry_run_needs_no_database(kind, monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert run(kind, "--dry-run") == 0
    assert "Skipped (invalid): 0" in capsys.readouterr().out


def test_cli_refuses_without_database_url(kind, monkeypatch, capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert run(kind) == 1
    assert "DATABASE_URL is not set" in capsys.readouterr().err
