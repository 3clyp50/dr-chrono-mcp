"""The drchrono_inbox_* MCP tools: build the voice graph and draft grounded replies, no creds."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from drchrono_mcp.inbox import mcp_tools

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


def test_draft_without_graph_returns_error() -> None:
    out = _run(mcp_tools.drchrono_inbox_draft_reply("subject", "body"))
    assert "error" in out


def test_live_source_is_gated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DRCHRONO_CLIENT_ID", raising=False)
    monkeypatch.delenv("DRCHRONO_CLIENT_SECRET", raising=False)
    out = _run(mcp_tools.drchrono_inbox_build_voice_graph(source="live"))
    assert "error" in out
