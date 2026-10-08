"""Grounded synthesis must never bypass Ask Ekiti evidence."""

import pytest

from app.services.ask_grounding import (
    GroundingError,
    build_evidence_packet,
    render_grounded_statements,
    synthesize_or_fallback,
    validate_synthesis,
)


STATEMENTS = [
    {
        "text": "Ekiti State was created on 1 October 1996.",
        "citation_index": 0,
    },
    {
        "text": "Ikogosi Warm Springs is in Ekiti West Local Government Area.",
        "citation_index": 1,
    },
]

CITATIONS = [
    {
        "doc_id": "history-state-creation-1996",
        "category": "history",
        "source_ids": ["SRC-001"],
        "source_titles": ["Official source"],
        "source_urls": ["https://example.org/history"],
        "evidence_status": "verified",
        "last_verified": "2026-09-29",
    },
    {
        "doc_id": "04-tourism-ikogosi-warm-springs",
        "category": "tourism",
        "source_ids": ["SRC-011"],
        "source_titles": ["Tourism source"],
        "source_urls": ["https://example.org/tourism"],
        "evidence_status": "needs_review",
        "last_verified": None,
    },
]


def packet():
    return build_evidence_packet(
        "When was Ekiti created and tell me about Ikogosi?",
        "en",
        STATEMENTS,
        CITATIONS,
    )


def test_evidence_packet_numbers_existing_citations():
    result = packet()

    assert result["evidence"][0]["id"] == 1
    assert result["evidence"][0]["doc_id"] == (
        "history-state-creation-1996"
    )

    assert result["evidence"][1]["id"] == 2
    assert result["evidence"][1]["source_ids"] == ["SRC-011"]

    assert "Use only the supplied evidence." in result["rules"]


def test_valid_structured_synthesis_is_rendered_with_backend_citations():
    value = {
        "statements": [
            {
                "text": "Ekiti State was created on 1 October 1996.",
                "citations": [1],
            },
            {
                "text": "Ikogosi Warm Springs is located in Ekiti West.",
                "citations": [2],
            },
        ]
    }

    validated = validate_synthesis(value, evidence_count=2)

    answer = render_grounded_statements(validated)

    assert answer == (
        "Ekiti State was created on 1 October 1996. [1]\n"
        "Ikogosi Warm Springs is located in Ekiti West. [2]"
    )


def test_unknown_evidence_reference_is_rejected():
    with pytest.raises(
        GroundingError,
        match="unknown evidence",
    ):
        validate_synthesis(
            {
                "statements": [
                    {
                        "text": "Unsupported claim.",
                        "citations": [3],
                    }
                ]
            },
            evidence_count=2,
        )


def test_uncited_generated_statement_is_rejected():
    with pytest.raises(
        GroundingError,
        match="requires evidence citations",
    ):
        validate_synthesis(
            {
                "statements": [
                    {
                        "text": "A factual claim.",
                        "citations": [],
                    }
                ]
            },
            evidence_count=2,
        )


def test_model_cannot_insert_its_own_citation_markers():
    with pytest.raises(
        GroundingError,
        match="must not contain citation markers",
    ):
        validate_synthesis(
            {
                "statements": [
                    {
                        "text": "Ekiti was created in 1996. [999]",
                        "citations": [1],
                    }
                ]
            },
            evidence_count=2,
        )


def test_invalid_generator_output_falls_back_to_sourced_answer():
    result = synthesize_or_fallback(
        lambda evidence: {
            "statements": [
                {
                    "text": "Invented claim.",
                    "citations": [99],
                }
            ]
        },
        packet(),
        "Safe sourced answer. [1]",
    )

    assert result["mode"] == "fallback"
    assert result["answer"] == "Safe sourced answer. [1]"


def test_generator_exception_falls_back_safely():
    def broken(_):
        raise RuntimeError("gateway unavailable")

    result = synthesize_or_fallback(
        broken,
        packet(),
        "Safe sourced answer. [1]",
    )

    assert result["mode"] == "fallback"
    assert result["answer"] == "Safe sourced answer. [1]"


def test_valid_generator_output_is_used():
    def generator(_):
        return {
            "statements": [
                {
                    "text": (
                        "Ekiti State was created on "
                        "1 October 1996."
                    ),
                    "citations": [1],
                },
                {
                    "text": (
                        "Ikogosi Warm Springs is located "
                        "in Ekiti West."
                    ),
                    "citations": [2],
                },
            ]
        }

    result = synthesize_or_fallback(
        generator,
        packet(),
        "Fallback answer.",
    )

    assert result["mode"] == "grounded"
    assert result["used_citations"] == [1, 2]
    assert "[1]" in result["answer"]
    assert "[2]" in result["answer"]
