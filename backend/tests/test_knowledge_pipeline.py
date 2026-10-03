"""Exercise the manifest-to-fact lifecycle without downloading a model."""
import csv
import hashlib
from pathlib import Path
from types import SimpleNamespace
import pytest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.base import Base
from app.models.knowledge import KnowledgeDocument, EMBEDDING_DIMENSIONS
from app.services.knowledge_pipeline import (
    _matching_doc_id,
    ingest_manifest,
    retrieve,
    verified_facts,
)

FIELDS = [
    "id", "path", "category", "status", "source_tier", "source_ids",
    "last_verified", "ask_ekiti_approved", "ask_ekiti_approved_by",
    "ask_ekiti_approved_date", "file_sha256", "ingestible"
]


def fixture(tmp_path: Path):
    root = tmp_path
    doc = root / "01_History" / "creation.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("""---
id: creation
status: verified
category: history
source_tier: A
source_ids: [SRC-001]
source_name: State announcement
source_url: https://example.org/announcement
verified_by: Reviewer
last_verified: 2026-09-21
---
## Facts
- Ekiti State was created on 1 October 1996. [S1]
## Sources
- [S1] SRC-001: State announcement. Government. https://example.org/announcement
""", encoding="utf-8")
    row = dict(id="creation", path="01_History/creation.md", category="history",
               status="verified", source_tier="A", source_ids="SRC-001",
               last_verified="2026-09-21", file_sha256=hashlib.sha256(doc.read_bytes()).hexdigest(),
               ingestible="yes")
    manifest = root / "13_Knowledge_Base" / "kb_manifest.csv"
    manifest.parent.mkdir()
    return root, doc, row, manifest


def write_manifest(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def embed(texts):
    return [[0.1] * EMBEDDING_DIMENSIONS for _ in texts]


@pytest.mark.parametrize('newline', ['\n', '\r\n', '\r'])
def test_ingests_explicit_line_endings(tmp_path, newline):
    root, doc, row, manifest = fixture(tmp_path)
    doc.write_bytes(doc.read_text().replace('\n', newline).encode('utf-8'))
    row['file_sha256'] = hashlib.sha256(doc.read_bytes()).hexdigest()
    write_manifest(manifest, [row])
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        result = ingest_manifest(manifest, root, db, embed)
        assert result['ingested'] == 1
        assert result['rejected'] == []


@pytest.mark.parametrize('content', ['', 'id: x\n---\n', '---\r\nid: x\r\n'])
def test_frontmatter_requires_both_delimiters(content):
    from app.services.knowledge_pipeline import _frontmatter
    with pytest.raises(ValueError, match='front matter'):
        _frontmatter(content)


@pytest.mark.parametrize('actual', ['vector(12)', 'vector', None])
def test_database_dimension_mismatch_is_rejected(actual):
    from app.services.knowledge_pipeline import check_embedding_dimensions
    db = SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name='postgresql')),
                         scalar=lambda statement: actual)
    with pytest.raises(RuntimeError, match='explicit migration'):
        check_embedding_dimensions(db)


def test_database_dimension_matches():
    from app.services.knowledge_pipeline import check_embedding_dimensions
    db = SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name='postgresql')),
                         scalar=lambda statement: f'vector({EMBEDDING_DIMENSIONS})')
    check_embedding_dimensions(db)


def test_retrieval_checks_database_dimension_after_embedding():
    answers = iter([1, 'vector(12)'])
    db = SimpleNamespace(
        bind=SimpleNamespace(dialect=SimpleNamespace(name='postgresql')),
        scalar=lambda statement: next(answers),
    )

    def query_embed(texts):
        return [[0.1] * EMBEDDING_DIMENSIONS for _ in texts]

    with pytest.raises(RuntimeError, match='explicit migration'):
        retrieve('Question?', db, embed=query_embed)


def test_settings_mutation_requires_restart(monkeypatch):
    from app.core.config import settings
    from app.services.knowledge_pipeline import check_embedding_dimensions
    monkeypatch.setattr(settings, 'EMBEDDING_DIMENSIONS', EMBEDDING_DIMENSIONS + 1)
    with pytest.raises(RuntimeError, match='restart'):
        check_embedding_dimensions(None)


def test_dimension_setting_at_import():
    import os
    import subprocess
    import sys
    env = dict(os.environ, EMBEDDING_DIMENSIONS='12', DATABASE_URL='sqlite:///:memory:')
    subprocess.run([sys.executable, '-c',
        'from app.models.knowledge import Chunk, EMBEDDING_DIMENSIONS; '
        'assert EMBEDDING_DIMENSIONS == 12; '
        'assert Chunk.__table__.c.embedding.type.dim == 12'], env=env, check=True)


@pytest.mark.parametrize('dimension', [0, -1])
def test_nonpositive_dimensions_rejected(dimension):
    from app.core.config import Settings
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Settings(EMBEDDING_DIMENSIONS=dimension)


def test_ingest_change_and_retire(tmp_path):
    root, doc, row, manifest = fixture(tmp_path)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        write_manifest(manifest, [row])
        assert ingest_manifest(manifest, root, db, embed)["ingested"] == 1
        assert ingest_manifest(manifest, root, db, embed)["unchanged"] == 1
        record = db.scalar(select(KnowledgeDocument))
        assert len(record.chunks) == 1
        assert record.chunks[0].source_ids == "SRC-001"
        assert record.chunks[0].source_urls == "https://example.org/announcement"
        doc.write_text(doc.read_text().replace("created on", "established on"))
        row["file_sha256"] = hashlib.sha256(doc.read_bytes()).hexdigest()
        write_manifest(manifest, [row])
        assert ingest_manifest(manifest, root, db, embed)["ingested"] == 1
        db.refresh(record)
        assert len(record.chunks) == 1
        assert "established" in record.chunks[0].content
        row["status"], row["ingestible"] = "retired", "no"
        write_manifest(manifest, [row])
        ingest_manifest(manifest, root, db, embed)
        db.refresh(record)
        assert not record.ingestible


def test_rejects_manifest_forgery_and_stale_hash(tmp_path):
    root, doc, row, manifest = fixture(tmp_path)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        row["file_sha256"] = "0" * 64
        write_manifest(manifest, [row])
        outcome = ingest_manifest(manifest, root, db, embed)
        assert "SHA-256" in outcome["rejected"][0]["reason"]
        assert db.scalar(select(KnowledgeDocument)) is None
        row["file_sha256"] = hashlib.sha256(doc.read_bytes()).hexdigest()
        doc.write_text(doc.read_text().replace("status: verified", "status: draft"))
        row["file_sha256"] = hashlib.sha256(doc.read_bytes()).hexdigest()
        write_manifest(manifest, [row])
        outcome = ingest_manifest(manifest, root, db, embed)
        assert "evidence status" in outcome["rejected"][0]["reason"]


def test_uncited_claim_is_rejected():
    from pytest import raises
    with raises(ValueError, match="citation"):
        verified_facts("## Facts\n- A claim without evidence.\n## Sources\n")


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        (
            "What is Arinta Waterfall?",
            "04-tourism-arinta-waterfall",
        ),
        (
            "What is Fajuyi Memorial Park?",
            "04-tourism-fajuyi-memorial-park",
        ),
        (
            "What is the Udiroko Festival?",
            "05-culture-udiroko-festival",
        ),
        (
            "What is the Ulerawa Health Programme?",
            "07-health-ulerawa-health-programme",
        ),
        (
            "What is Ikogosi Warm Springs?",
            "04-tourism-ikogosi-warm-springs",
        ),
    ],
)
def test_named_subject_resolves_to_exact_document(question, expected):
    doc_ids = [
        "04-tourism-arinta-waterfall",
        "04-tourism-fajuyi-memorial-park",
        "04-tourism-ikogosi-warm-springs",
        "05-culture-udiroko-festival",
        "07-health-ulerawa-health-programme",
    ]

    assert _matching_doc_id(question, doc_ids) == expected


def test_broad_topic_question_does_not_focus_one_document():
    doc_ids = [
        "04-tourism-arinta-waterfall",
        "04-tourism-fajuyi-memorial-park",
        "04-tourism-ikogosi-warm-springs",
    ]

    assert (
        _matching_doc_id(
            "Tell me about tourism in Ekiti",
            doc_ids,
        )
        is None
    )


def test_empty_corpus_returns_no_hits_after_query_embedding():
    class EmptyPostgresSession:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def scalar(self, statement):
            return None

    calls = []

    def query_embed(texts):
        calls.append(texts)
        return [[0.1] * EMBEDDING_DIMENSIONS for _ in texts]

    assert retrieve(
        "When was Ekiti State created?",
        EmptyPostgresSession(),
        embed=query_embed,
    ) == []

    assert calls == [["When was Ekiti State created?"]]


def test_ask_route_cites_each_returned_fact(client, monkeypatch):
    from app.api.routes import ask_ekiti
    hit = {"doc_id": "history-state-creation-1996", "content": "Ekiti State was created in 1996.",
           "source_ids": ["SRC-001"], "source_titles": ["State announcement"],
           "source_urls": ["https://example.org/announcement"],
           "source_url": "https://example.org/announcement", "category": "history",
           "tier": "A", "last_verified": "2026-09-21", "path": "01_History/creation.md"}
    monkeypatch.setattr(ask_ekiti, "retrieve", lambda *args, **kwargs: [hit])
    response = client.post("/api/ask-ekiti", json={"question": "When was Ekiti State created?"})
    assert response.status_code == 200
    assert response.json()["citations"][0]["source_ids"] == ["SRC-001"]
    assert response.json()["citations"][0]["tier"] == "A"
    assert client.post("/api/ask-ekiti", json={"question": "When?", "language": "yo"}).status_code == 503


def test_ask_route_declines_without_evidence(client, monkeypatch):
    from app.api.routes import ask_ekiti
    monkeypatch.setattr(ask_ekiti, "retrieve", lambda *args, **kwargs: [])
    response = client.post("/api/ask-ekiti", json={"question": "Unknown question"})
    assert response.json()["answer_status"] == "insufficient"
    assert response.json()["citations"] == []


def test_ingests_explicitly_approved_needs_review_document(tmp_path):
    root = tmp_path
    doc = root / "04_Tourism" / "ikogosi.md"
    doc.parent.mkdir(parents=True)

    doc.write_text("""---
id: ikogosi
status: needs_review
category: tourism
source_tier: A
source_ids: [SRC-011]
source_name: Tourism source
source_url: https://example.org/tourism
ask_ekiti_approved: true
ask_ekiti_approved_by: Reviewer
ask_ekiti_approved_date: 2026-10-01
---
## Facts
- Ikogosi has warm and cold springs. [S1]
## Sources
- [S1] SRC-011: Tourism source. Government. https://example.org/tourism
""", encoding="utf-8")

    row = dict(
        id="ikogosi",
        path="04_Tourism/ikogosi.md",
        category="tourism",
        status="needs_review",
        source_tier="A",
        source_ids="SRC-011",
        last_verified="",
        ask_ekiti_approved="yes",
        ask_ekiti_approved_by="Reviewer",
        ask_ekiti_approved_date="2026-10-01",
        file_sha256=hashlib.sha256(doc.read_bytes()).hexdigest(),
        ingestible="yes",
    )

    manifest = root / "13_Knowledge_Base" / "kb_manifest.csv"
    manifest.parent.mkdir()

    write_manifest(manifest, [row])

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        result = ingest_manifest(manifest, root, db, embed)

        assert result["ingested"] == 1
        assert result["rejected"] == []

        record = db.scalar(select(KnowledgeDocument))

        assert record.doc_id == "ikogosi"
        assert record.evidence_status == "needs_review"
        assert record.last_verified is None
        assert record.ask_ekiti_approved is True
        assert record.ask_ekiti_approved_date.isoformat() == "2026-10-01"
        assert len(record.chunks) == 1
