"""Provider-neutral entry point for Ask Ekiti grounded synthesis."""

from collections.abc import Callable
from typing import Any

from app.core.config import settings

GroundedSynthesizer = Callable[[dict[str, Any]], dict[str, Any]]


def get_grounded_synthesizer() -> GroundedSynthesizer | None:
    """Return the configured grounded-answer generator.

    Grounded synthesis is deliberately opt-in. Until the external gateway
    request/response contract is confirmed, Ask Ekiti keeps using the
    deterministic cited-fact composer.

    A provider implementation can later be attached here without changing
    the planner, retrieval, grounding validator, or answer composer.
    """
    if not settings.ASK_EKITI_SYNTHESIS_ENABLED:
        return None

    if not settings.ASK_EKITI_LLM_WEBHOOK_URL:
        raise RuntimeError(
            "Ask Ekiti synthesis is enabled but "
            "ASK_EKITI_LLM_WEBHOOK_URL is not configured"
        )

    if not settings.ASK_EKITI_LLM_WEBHOOK_KEY:
        raise RuntimeError(
            "Ask Ekiti synthesis is enabled but "
            "ASK_EKITI_LLM_WEBHOOK_KEY is not configured"
        )

    if not settings.LLM_MODEL:
        raise RuntimeError(
            "Ask Ekiti synthesis is enabled but LLM_MODEL is not configured"
        )

    # Do not guess the gateway payload contract.
    raise RuntimeError(
        "Ask Ekiti synthesis gateway contract has not yet been configured"
    )
