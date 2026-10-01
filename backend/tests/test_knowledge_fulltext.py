"""Free-plan retrieval must not invoke the embedding runtime."""
from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.services.knowledge_fulltext import retrieve_fulltext, search_text
from app.services.knowledge_pipeline import retrieve


def test_fulltext_preserves_citations_without_embedding(monkeypatch):
    monkeypatch.setattr(settings, "ASK_EKITI_RETRIEVAL_MODE", "fulltext")
    row = dict(doc_id="creation", content="Ekiti State was created on 1 October 1996.",
               category="history", tier="A", last_verified=date(2026, 9, 29),
               path="01_History/state-creation-1996.md", source_url="https://example.org",
               source_ids="SRC-001", source_titles="Government statement",
               source_urls="https://example.org", search_rank=0.1)
    captured = {}

    def execute(statement, parameters):
        captured.update(parameters)
        return SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: [row]))

    def forbidden(*args, **kwargs):
        pytest.fail("Fulltext must not load embeddings or check vector dimensions")

    monkeypatch.setattr("app.services.knowledge_pipeline.check_embedding_dimensions", forbidden)
    db = SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
                         execute=execute, scalar=forbidden)
    hits = retrieve("When was Ekiti State created?", db, embed=forbidden, category="history")
    assert hits[0]["source_ids"] == ["SRC-001"]
    assert hits[0]["source_urls"] == ["https://example.org"]
    assert hits[0]["last_verified"] == "2026-09-29"
    assert hits[0]["content"] == row["content"]
    assert captured["category"] == "history"


def test_empty_fulltext_results_do_not_fall_back(monkeypatch):
    monkeypatch.setattr(settings, "ASK_EKITI_RETRIEVAL_MODE", "fulltext")
    db = SimpleNamespace(bind=SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
                         execute=lambda *args: SimpleNamespace(
                             mappings=lambda: SimpleNamespace(all=lambda: [])))
    def forbidden(*args):
        pytest.fail("No fallback model may be loaded")
    assert retrieve("Population in 2026?", db, embed=forbidden) == []


def test_lga_alias_preserves_specific_terms():
    assert search_text("What is the headquarters of Ikere LGA?") == (
        "What is the headquarters of Ikere local government area?")
    assert "2026" in search_text("Ekiti population in 2026?")
    assert search_text("Ise/Orun") == "Ise/Orun"


def test_search_input_is_bound_not_interpolated():
    question = "'; DROP TABLE chunks; --"
    def execute(statement, parameters):
        assert question not in str(statement)
        assert parameters["question"] == question
        return SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: []))
    assert retrieve_fulltext(question, SimpleNamespace(execute=execute)) == []


def test_invalid_mode_is_rejected():
    with pytest.raises(ValidationError):
        Settings(ASK_EKITI_RETRIEVAL_MODE="fultext")


@pytest.fixture
def postgres_search_db():
    """Optional real SQL check, isolated in temporary tables on a TEST database."""
    import os
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    url = os.environ.get("ASK_EKITI_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ASK_EKITI_TEST_DATABASE_URL to a dedicated PostgreSQL test DB")
    engine = create_engine(url)
    with engine.connect() as conn:
        transaction = conn.begin()
        conn.execute(text("""CREATE TEMP TABLE knowledge_documents (
            id integer,
            doc_id text,
            class text,
            tier text,
            last_verified date,
            evidence_status text,
            ask_ekiti_approved boolean,
            ask_ekiti_approved_date date,
            path text,
            source_url text,
            ingestible boolean
        ) ON COMMIT DROP"""))
        conn.execute(text("""CREATE TEMP TABLE chunks (
            document_id integer, chunk_index integer, content text,
            source_ids text, source_titles text, source_urls text) ON COMMIT DROP"""))
        fixtures = [
            (1, "creation", "history", True, "verified", False,
             "Ekiti State was created on 1 October 1996.", "SRC-001"),
            (2, "ikere", "lgas", True, "verified", False,
             "Ikere Local Government Area's headquarters is Ikere-Ekiti.", "SRC-028"),
            (3, "moba", "lgas", True, "verified", False,
             "Moba Local Government Area is one of the 16 Local Government Areas of Ekiti State.", "SRC-028"),
            (4, "draft", "statistics", False, "needs_review", False,
             "Ekiti State population in 2026 is 999.", "SRC-999"),
            (5, "uncited", "statistics", True, "verified", False,
             "Ekiti State population in 2026 is 123.", ""),
            (6, "ikogosi", "tourism", True, "needs_review", True,
             "Ikogosi Warm Springs is located in Ekiti West Local Government Area.", "SRC-011"),
        ]

        for ident, doc_id, category, ingestible, evidence_status, ask_approved, content, source in fixtures:
            conn.execute(text("""
                INSERT INTO knowledge_documents (
                    id, doc_id, class, tier, last_verified,
                    evidence_status, ask_ekiti_approved,
                    ask_ekiti_approved_date, path, source_url, ingestible
                )
                VALUES (
                    :id, :doc_id, :category, 'A',
                    CASE WHEN :evidence_status = 'verified'
                         THEN CURRENT_DATE ELSE NULL END,
                    :evidence_status,
                    :ask_approved,
                    CASE WHEN :ask_approved
                         THEN CURRENT_DATE ELSE NULL END,
                    'test.md',
                    'https://example.org',
                    :ingestible
                )
            """), dict(
                id=ident,
                doc_id=doc_id,
                category=category,
                ingestible=ingestible,
                evidence_status=evidence_status,
                ask_approved=ask_approved,
            ))
            conn.execute(text("""INSERT INTO chunks VALUES
                (:id, 0, :content, :source, 'Government', 'https://example.org')"""),
                dict(id=ident, content=content, source=source))
        with Session(bind=conn) as db:
            yield db
        transaction.rollback()
    engine.dispose()


@pytest.mark.parametrize("question,category,expected", [
    ("When was Ekiti State created?", None, ["creation"]),
    ("What is the headquarters of Ikere LGA?", None, ["ikere"]),
    ("What is the headquarters of Moba LGA?", None, []),
    ("What is Ekiti State population in 2026?", None, []),
    ("When was Ekiti State created?", "lgas", []),
    ("Ikogosi Warm Springs", "tourism", ["ikogosi"]),
    ("the and is", None, []),
    ("'; DROP TABLE chunks; --", None, []),
])
def test_postgres_search_rules(postgres_search_db, question, category, expected):
    assert [h["doc_id"] for h in retrieve_fulltext(
        question, postgres_search_db, category=category)] == expected
