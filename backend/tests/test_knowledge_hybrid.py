"""Hybrid Ask Ekiti retrieval combines semantic and lexical evidence."""

from app.core.config import settings
from app.services.knowledge_pipeline import (
    _retrieval_focus,
    fuse_hybrid_hits,
    retrieve,
)


def hit(doc_id, content, **extra):
    value = {
        "doc_id": doc_id,
        "content": content,
        "category": "tourism",
        "source_ids": ["SRC-001"],
        "source_titles": ["Source"],
        "source_urls": ["https://example.org"],
    }
    value.update(extra)
    return value


def test_hybrid_fusion_boosts_fact_found_by_both_methods():
    common = "Ikogosi Warm Springs is located in Ekiti West Local Government Area."

    vector = [
        hit("ikogosi", common, distance=0.20),
        hit("arinta", "Arinta Waterfall is in Ekiti State.", distance=0.25),
    ]

    fulltext = [
        hit("ikogosi", common, search_rank=0.8),
        hit("fajuyi", "Fajuyi Memorial Park is in Ado-Ekiti.", search_rank=0.5),
    ]

    result = fuse_hybrid_hits(vector, fulltext, limit=3)

    assert result[0]["doc_id"] == "ikogosi"
    assert result[0]["retrieval_sources"] == ["fulltext", "vector"]

    assert {item["doc_id"] for item in result} == {
        "ikogosi",
        "arinta",
        "fajuyi",
    }


def test_explicit_doc_ids_disable_single_document_focus():
    eligible = [
        "lga-ado-ekiti",
        "lga-ikere",
    ]

    assert _retrieval_focus(
        "Compare Ado-Ekiti and Ikere LGAs.",
        eligible,
        requested_doc_ids=eligible,
    ) is None


def test_named_subject_still_focuses_when_planner_has_no_doc_ids():
    eligible = [
        "04-tourism-arinta-waterfall",
        "04-tourism-ikogosi-warm-springs",
    ]

    assert _retrieval_focus(
        "Tell me about Ikogosi Warm Springs.",
        eligible,
    ) == "04-tourism-ikogosi-warm-springs"


def test_hybrid_mode_calls_both_retrievers(monkeypatch):
    vector = [
        hit(
            "ikogosi",
            "Ikogosi Warm Springs is in Ekiti West.",
            distance=0.2,
        )
    ]
    lexical = [
        hit(
            "arinta",
            "Arinta Waterfall is in Ekiti State.",
            search_rank=0.6,
        )
    ]

    vector_calls = []
    text_calls = []

    def fake_vector(question, db, **kwargs):
        vector_calls.append((question, kwargs))
        return vector

    def fake_fulltext(question, db, **kwargs):
        text_calls.append((question, kwargs))
        return lexical

    monkeypatch.setattr(
        "app.services.knowledge_pipeline.retrieve_vector",
        fake_vector,
    )
    monkeypatch.setattr(
        "app.services.knowledge_fulltext.retrieve_fulltext",
        fake_fulltext,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_RETRIEVAL_MODE",
        "hybrid",
    )

    result = retrieve(
        "Tourism in Ekiti",
        object(),
        limit=2,
        category="tourism",
    )

    assert len(vector_calls) == 1
    assert len(text_calls) == 1
    assert {item["doc_id"] for item in result} == {
        "ikogosi",
        "arinta",
    }

    assert vector_calls[0][1]["category"] == "tourism"
    assert text_calls[0][1]["category"] == "tourism"
