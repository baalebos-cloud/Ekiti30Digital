"""Ask Ekiti synthesis must remain opt-in and fail closed."""

import pytest

from app.core.config import settings
from app.services.ask_synthesizer import get_grounded_synthesizer


def test_synthesis_disabled_returns_no_generator(monkeypatch):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        False,
    )

    assert get_grounded_synthesizer() is None


@pytest.mark.parametrize(
    ("setting", "message"),
    [
        (
            "ASK_EKITI_LLM_WEBHOOK_URL",
            "ASK_EKITI_LLM_WEBHOOK_URL",
        ),
        (
            "ASK_EKITI_LLM_WEBHOOK_KEY",
            "ASK_EKITI_LLM_WEBHOOK_KEY",
        ),
        (
            "LLM_MODEL",
            "LLM_MODEL",
        ),
    ],
)
def test_enabled_synthesis_requires_configuration(
    monkeypatch,
    setting,
    message,
):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )

    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://example.org/gateway",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "LLM_MODEL",
        "example-model",
    )

    monkeypatch.setattr(settings, setting, None)

    with pytest.raises(RuntimeError, match=message):
        get_grounded_synthesizer()


def test_configured_but_unimplemented_gateway_fails_closed(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_SYNTHESIS_ENABLED",
        True,
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_URL",
        "https://example.org/gateway",
    )
    monkeypatch.setattr(
        settings,
        "ASK_EKITI_LLM_WEBHOOK_KEY",
        "secret",
    )
    monkeypatch.setattr(
        settings,
        "LLM_MODEL",
        "example-model",
    )

    with pytest.raises(
        RuntimeError,
        match="gateway contract",
    ):
        get_grounded_synthesizer()


def _creation_hit():
    return {
        "doc_id": "history-state-creation-1996",
        "content": "Ekiti State was created on 1 October 1996.",
        "category": "history",
        "source_ids": ["SRC-001"],
        "source_titles": ["Official creation source"],
        "source_urls": ["https://example.org/creation"],
        "source_url": "https://example.org/creation",
        "tier": "A",
        "last_verified": "2026-09-29",
        "evidence_status": "verified",
        "ask_ekiti_approved": False,
        "ask_ekiti_approved_date": None,
        "path": "01_History/state-creation-1996.md",
    }


def test_api_uses_valid_grounded_synthesizer(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [_creation_hit()],
    )

    def synthesizer(packet):
        assert packet["question"] == "When was Ekiti State created?"
        assert packet["evidence"][0]["id"] == 1

        return {
            "statements": [
                {
                    "text": (
                        "Ekiti State came into existence "
                        "on 1 October 1996."
                    ),
                    "citations": [1],
                }
            ]
        }

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: synthesizer,
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "When was Ekiti State created?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["synthesis_mode"] == "grounded"
    assert (
        "Ekiti State came into existence "
        "on 1 October 1996. [1]"
        in payload["answer"]
    )
    assert payload["citations"][0]["source_ids"] == ["SRC-001"]


def test_api_invalid_synthesis_falls_back_safely(
    client,
    monkeypatch,
):
    from app.api.routes import ask_ekiti

    monkeypatch.setattr(
        ask_ekiti,
        "retrieve",
        lambda *args, **kwargs: [_creation_hit()],
    )

    def invalid_synthesizer(_packet):
        return {
            "statements": [
                {
                    "text": "Ekiti was created by an unsupported person.",
                    "citations": [99],
                }
            ]
        }

    monkeypatch.setattr(
        ask_ekiti,
        "get_grounded_synthesizer",
        lambda: invalid_synthesizer,
    )

    response = client.post(
        "/api/ask-ekiti",
        json={
            "question": "When was Ekiti State created?",
            "language": "en",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["synthesis_mode"] == "fallback"
    assert (
        "Ekiti State was created on 1 October 1996. [1]"
        in payload["answer"]
    )
    assert "unsupported person" not in payload["answer"]
