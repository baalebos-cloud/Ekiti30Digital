"""Citation-safe contract for grounded Ask Ekiti answer synthesis."""

import re

MAX_SYNTHESIS_STATEMENTS = 12
MAX_STATEMENT_LENGTH = 1000

INLINE_CITATION_RE = re.compile(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]")


class GroundingError(ValueError):
    """Raised when generated synthesis violates the grounding contract."""


def build_evidence_packet(
    question,
    language,
    statements,
    citations,
):
    """Build the only factual context an answer generator may use.

    Evidence IDs are one-based and correspond directly to Ask Ekiti's
    citation array. The generator receives sourced facts, not the raw
    knowledge base or permission to answer from model memory.
    """
    evidence = []

    for statement in statements:
        citation_index = statement.get("citation_index")

        if (
            not isinstance(citation_index, int)
            or isinstance(citation_index, bool)
            or citation_index < 0
            or citation_index >= len(citations)
        ):
            raise GroundingError("statement references an invalid citation")

        citation = citations[citation_index]

        evidence.append(
            {
                "id": citation_index + 1,
                "fact": statement["text"],
                "doc_id": citation.get("doc_id"),
                "category": citation.get("category"),
                "source_ids": citation.get("source_ids") or [],
                "source_titles": citation.get("source_titles") or [],
                "source_urls": citation.get("source_urls") or [],
                "evidence_status": citation.get("evidence_status"),
                "last_verified": citation.get("last_verified"),
            }
        )

    return {
        "question": question,
        "language": language,
        "rules": [
            "Use only the supplied evidence.",
            "Do not add facts from model memory or outside knowledge.",
            "Every generated factual statement must cite at least one evidence ID.",
            "Do not invent evidence IDs.",
            "If evidence does not support a requested detail, do not guess it.",
            "Return structured statements, not citation markers inside the text.",
        ],
        "evidence": evidence,
        "output_schema": {
            "statements": [
                {
                    "text": "A concise statement supported by the evidence.",
                    "citations": [1],
                }
            ]
        },
    }


def validate_synthesis(value, evidence_count):
    """Validate structured model output before it can reach the user."""
    if not isinstance(value, dict):
        raise GroundingError("synthesis output must be an object")

    statements = value.get("statements")

    if not isinstance(statements, list) or not statements:
        raise GroundingError("synthesis must contain statements")

    if len(statements) > MAX_SYNTHESIS_STATEMENTS:
        raise GroundingError("too many synthesis statements")

    validated = []
    seen_text = set()

    for item in statements:
        if not isinstance(item, dict):
            raise GroundingError("each synthesis statement must be an object")

        text = item.get("text")
        citations = item.get("citations")

        if not isinstance(text, str) or not text.strip():
            raise GroundingError("synthesis statement text is required")

        text = text.strip()

        if len(text) > MAX_STATEMENT_LENGTH:
            raise GroundingError("synthesis statement is too long")

        # Citation rendering belongs to our backend, not the model.
        if INLINE_CITATION_RE.search(text):
            raise GroundingError(
                "synthesis text must not contain citation markers"
            )

        if not isinstance(citations, list) or not citations:
            raise GroundingError(
                "every synthesis statement requires evidence citations"
            )

        normalized_citations = []

        for citation in citations:
            if (
                not isinstance(citation, int)
                or isinstance(citation, bool)
                or citation < 1
                or citation > evidence_count
            ):
                raise GroundingError(
                    "synthesis references unknown evidence"
                )

            if citation not in normalized_citations:
                normalized_citations.append(citation)

        key = text.casefold()

        if key in seen_text:
            raise GroundingError("duplicate synthesis statement")

        seen_text.add(key)

        validated.append(
            {
                "text": text,
                "citations": normalized_citations,
            }
        )

    return validated


def render_grounded_statements(statements):
    """Render validated statements with backend-controlled citations."""
    lines = []

    for statement in statements:
        markers = " ".join(
            f"[{citation}]"
            for citation in statement["citations"]
        )

        lines.append(
            f"{statement['text']} {markers}"
        )

    return "\n".join(lines)


def synthesize_or_fallback(
    synthesizer,
    packet,
    fallback_answer,
):
    """Use grounded synthesis only when it passes all validation.

    Any generator failure or contract violation returns the existing
    deterministic Ask Ekiti answer instead of exposing unsupported output.
    """
    if synthesizer is None:
        return {
            "answer": fallback_answer,
            "mode": "fallback",
            "used_citations": [],
        }

    try:
        raw = synthesizer(packet)

        validated = validate_synthesis(
            raw,
            evidence_count=len(packet["evidence"]),
        )

        used = []

        for statement in validated:
            for citation in statement["citations"]:
                if citation not in used:
                    used.append(citation)

        return {
            "answer": render_grounded_statements(validated),
            "mode": "grounded",
            "used_citations": used,
            "statements": validated,
        }

    except Exception:
        # Fail closed: never expose invalid or ungrounded model output.
        return {
            "answer": fallback_answer,
            "mode": "fallback",
            "used_citations": [],
        }
