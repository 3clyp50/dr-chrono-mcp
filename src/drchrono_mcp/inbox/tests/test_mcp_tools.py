"""The drchrono_inbox_* MCP tools: build the voice graph and draft grounded replies, no creds."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from drchrono_mcp.inbox import mcp_tools
from drchrono_mcp.inbox.interfaces import ResponseFacts

_INCOMING_SUBJECT = "Lab result available"
_INCOMING_BODY = (
    "Gestational glucose screening, 1-hour, result 197 mg/dL for prenatal patient (cutoff < 140)."
)


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def _isolated_data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    monkeypatch.setenv("INBOX_DATA_DIR", str(tmp_path))


def test_build_then_draft_grounds_canonical_case() -> None:
    built = _run(mcp_tools.drchrono_inbox_build_voice_graph(n=60))
    assert built["built"] and built["messages"] == 60

    status = _run(mcp_tools.drchrono_inbox_status())
    assert status["graph_ready"] and status["corpus_count"] == 60

    out = _run(mcp_tools.drchrono_inbox_draft_reply(_INCOMING_SUBJECT, _INCOMING_BODY))
    assert out["matched"]["topic"] == "gestational_glucose"
    assert out["matched"]["normalcy"] == "abnormal"
    assert "OGTT" in (out["suggested_action"] or "")
    assert out["needs_review"] is False
    assert "Next Steps" in out["draft"]
    assert out["voice_exemplars"]


def test_rebuild_does_not_double_action_weights() -> None:
    _run(mcp_tools.drchrono_inbox_build_voice_graph(n=10))
    _run(mcp_tools.drchrono_inbox_build_voice_graph(n=10))  # reset must prevent double-count

    out = _run(mcp_tools.drchrono_inbox_draft_reply(_INCOMING_SUBJECT, _INCOMING_BODY))
    ogtt = [a for a in out["action_support"] if "OGTT" in a["action"]]
    assert ogtt and ogtt[0]["weight"] == 1


def test_review_gate_requires_complete_facts_even_for_high_score() -> None:
    incoming = ResponseFacts(topic="gestational_glucose", normalcy="abnormal")
    high_score_hit = {"score": 0.99}

    assert mcp_tools._needs_review(
        top=high_score_hit,
        incoming=incoming,
        matched_topic="gestational_glucose",
        matched_normalcy="abnormal",
        suggested_action=None,
    )
    assert mcp_tools._needs_review(
        top=high_score_hit,
        incoming=incoming,
        matched_topic="gestational_glucose",
        matched_normalcy="unknown",
        suggested_action="Schedule a 3-hour OGTT",
    )
    assert not mcp_tools._needs_review(
        top=high_score_hit,
        incoming=incoming,
        matched_topic="gestational_glucose",
        matched_normalcy="abnormal",
        suggested_action="Schedule a 3-hour OGTT",
    )
    incoming_normal = ResponseFacts(topic="gestational_glucose", normalcy="normal")
    assert not mcp_tools._needs_review(
        top=high_score_hit,
        incoming=incoming_normal,
        matched_topic="gestational_glucose",
        matched_normalcy="normal",
        suggested_action=None,
    )


def test_suggested_action_uses_usual_action_fallback() -> None:
    assert (
        mcp_tools._suggested_action(
            {
                "action": None,
                "usual_action": "schedule follow-up testing",
                "topic_actions": [{"action": "less preferred action", "weight": 1}],
            }
        )
        == "schedule follow-up testing"
    )


def test_draft_without_graph_returns_error() -> None:
    out = _run(mcp_tools.drchrono_inbox_draft_reply("subject", "body"))
    assert "error" in out


def test_live_source_is_gated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DRCHRONO_CLIENT_ID", raising=False)
    monkeypatch.delenv("DRCHRONO_CLIENT_SECRET", raising=False)
    out = _run(mcp_tools.drchrono_inbox_build_voice_graph(source="live"))
    assert "error" in out
