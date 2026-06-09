"""Live corpus builder robustness checks."""

from __future__ import annotations

import asyncio

import pytest

from drchrono_mcp.inbox.config import InboxConfig
from drchrono_mcp.inbox.corpus.builder import CorpusBuilder


class _FakeClient:
    def __init__(self, responses: list[dict | None]) -> None:
        self.responses = responses

    async def get(self, endpoint: str, params: dict | None = None) -> dict | None:
        return self.responses.pop(0)


def test_build_live_handles_missing_current_user(tmp_path) -> None:
    builder = CorpusBuilder(InboxConfig(data_dir=tmp_path), _FakeClient([None]))

    with pytest.raises(RuntimeError, match="Cannot determine doctor_id"):
        asyncio.run(builder.build_live())


def test_build_live_stops_on_empty_page_response(tmp_path) -> None:
    builder = CorpusBuilder(
        InboxConfig(data_dir=tmp_path, doctor_id=123),
        _FakeClient([None]),
    )

    assert asyncio.run(builder.build_live()) == 0
    assert builder.store.count() == 0
