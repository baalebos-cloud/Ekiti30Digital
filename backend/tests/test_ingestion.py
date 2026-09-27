"""Tests for the Ask Ekiti ingestion pipeline (app/services/ingestion.py).

Uses an in-memory SQLite database for every test — never the real dev.db.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.knowledge import KnowledgeDocument
from app.services.ingestion import ingest_documents, load_manifest

SAMPLE_MANIFEST = os.path.join(
    os.path.dirname(__file__),
    "..",
    "app",
    "services",
    "sample_data",
    "sample_manifest.csv",
)


def make_row(**overrides) -> dict:
    """A valid ingestible row, keyed by internal names as load_manifest returns."""
    row = {
        "doc_id": "doc-001",
        "path": "01_History/doc-001.md",
        "class_": "history",
        "tier": "A",
        "last_verified": "2026-01-15",
        "ingestible": "yes",
        "file_sha256": "abc123",
    }
    row.update(overrides)
    return row


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_load_manifest_filters_ingestible_rows():
    rows = load_manifest(SAMPLE_MANIFEST)

    # Only "yes" (case-insensitive) rows should come back; the sample file
    # has two "no"/"No" rows mixed in specifically to exercise this.
    assert {row["doc_id"] for row in rows} == {"sample-001", "sample-003", "sample-005"}
    assert all(row["ingestible"].strip().lower() == "yes" for row in rows)


def test_load_manifest_maps_columns_to_internal_names():
    row = load_manifest(SAMPLE_MANIFEST)[0]

    assert row["doc_id"] == "sample-001"
    assert row["class_"] == "history"
    assert row["tier"] == "A"
    assert row["path"] == "01_History/history-of-ekiti.md"
    assert "id" not in row and "category" not in row and "source_tier" not in row


def test_ingest_documents_creates_rows(db_session: Session):
    rows = load_manifest(SAMPLE_MANIFEST)

    result = ingest_documents(rows, db_session)

    assert result.ingested == len(rows) == 3
    assert result.skipped == []
    assert db_session.query(KnowledgeDocument).count() == 3

    doc = db_session.query(KnowledgeDocument).filter_by(doc_id="sample-001").one()
    assert doc.class_ == "history"
    assert doc.tier == "A"
    assert doc.ingestible is True
    assert doc.path == "01_History/history-of-ekiti.md"
    assert doc.file_sha256 == "1" * 64
    # Not in the manifest; left null until looked up elsewhere.
    assert doc.source_title is None
    assert doc.source_url is None


def test_ingest_documents_upserts_without_duplicating(db_session: Session):
    rows = load_manifest(SAMPLE_MANIFEST)

    first = ingest_documents(rows, db_session)
    second = ingest_documents(rows, db_session)

    assert first.ingested == second.ingested == 3
    assert db_session.query(KnowledgeDocument).count() == 3


def test_ingest_documents_updates_changed_fields(db_session: Session):
    ingest_documents([make_row()], db_session)

    ingest_documents(
        [make_row(tier="B", last_verified="2026-06-30", file_sha256="def456")],
        db_session,
    )

    db_session.expire_all()
    doc = db_session.query(KnowledgeDocument).filter_by(doc_id="doc-001").one()
    assert doc.tier == "B"
    assert doc.last_verified.isoformat() == "2026-06-30"
    assert doc.file_sha256 == "def456"
    assert db_session.query(KnowledgeDocument).count() == 1


def test_ingest_documents_skips_row_missing_required_field(db_session: Session):
    rows = [make_row(), make_row(doc_id="doc-002", class_="")]

    result = ingest_documents(rows, db_session)

    assert result.ingested == 1
    assert len(result.skipped) == 1
    assert result.skipped[0].doc_id == "doc-002"
    assert "class_" in result.skipped[0].reason
    assert db_session.query(KnowledgeDocument).filter_by(doc_id="doc-002").count() == 0


def test_ingest_documents_skips_row_with_invalid_date(db_session: Session):
    rows = [make_row(), make_row(doc_id="doc-002", last_verified="15/01/2026")]

    result = ingest_documents(rows, db_session)

    assert result.ingested == 1
    assert [s.doc_id for s in result.skipped] == ["doc-002"]
    assert "last_verified" in result.skipped[0].reason


def test_ingest_documents_skips_duplicate_doc_ids_in_batch(db_session: Session):
    rows = [
        make_row(doc_id="doc-001"),
        make_row(doc_id="doc-002", tier="A"),
        make_row(doc_id="doc-002", tier="B"),
    ]

    result = ingest_documents(rows, db_session)

    assert result.ingested == 1
    assert [s.doc_id for s in result.skipped] == ["doc-002", "doc-002"]
    assert all("duplicate" in s.reason for s in result.skipped)
    assert db_session.query(KnowledgeDocument).filter_by(doc_id="doc-002").count() == 0
