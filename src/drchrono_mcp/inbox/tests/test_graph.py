"""Response-graph retrieval must return the doctor's voice + next action for a new message."""

from __future__ import annotations

from pathlib import Path

import pytest

from drchrono_mcp.inbox.corpus.synthetic import generate
from drchrono_mcp.inbox.embed import HashingEmbedder
from drchrono_mcp.inbox.extract import HeuristicExtractor
from drchrono_mcp.inbox.graph.ingest import GraphIngestor
from drchrono_mcp.inbox.graph.memory_store import InMemoryGraphStore
from drchrono_mcp.inbox.interfaces import ResponseFacts

_INCOMING = (
    "Lab result available for prenatal patient: "
    "Gestational glucose screening, 1-hour, result 197 mg/dL (cutoff < 140)."
)


def _ingest(store: InMemoryGraphStore, n: int = 60) -> None:
    GraphIngestor(store, HashingEmbedder(), HeuristicExtractor()).ingest(generate(n))


def test_canonical_case_grounds_voice_and_action() -> None:
    store = InMemoryGraphStore()
    _ingest(store)
    hits = store.query(HashingEmbedder().embed([_INCOMING])[0], top_k=3)

    assert hits
    top = hits[0]
    assert top["topic"] == "gestational_glucose"
    assert top["normalcy"] == "abnormal"
    assert top["demographic"] == "prenatal"
    assert "OGTT" in (top["action"] or "")
    # The action is aggregated and weighted across all gestational messages, not one-off.
    assert any("OGTT" in a["action"] and a["weight"] > 1 for a in top["topic_actions"])
    # Voice grounding: the exemplar is the physician-style sent wording.
    assert "Next Steps" in top["body"]


def test_ingest_stats_cover_all_topics() -> None:
    store = InMemoryGraphStore()
    stats = GraphIngestor(store, HashingEmbedder(), HeuristicExtractor()).ingest(generate(60))
    assert stats.messages == 60
    assert stats.topics >= 8
    assert stats.actions >= 6


def test_hit_action_is_phrase_specific_with_usual_action_fallback() -> None:
    store = InMemoryGraphStore()
    store.add_message(
        message_id="normal-no-action",
        subject="Normal shared topic",
        body="Everything looks reassuring.",
        facts=ResponseFacts(
            topic="shared_topic",
            normalcy="normal",
            phrase_key="shared_topic:normal",
        ),
        embedding=[1.0, 0.0],
    )
    store.add_message(
        message_id="abnormal-with-action",
        subject="Abnormal shared topic",
        body="Please schedule follow-up testing.",
        facts=ResponseFacts(
            topic="shared_topic",
            normalcy="abnormal",
            action="schedule follow-up testing",
            phrase_key="shared_topic:abnormal",
        ),
        embedding=[0.0, 1.0],
    )

    hit = store.query([1.0, 0.0], top_k=1)[0]

    assert hit["action"] is None
    assert hit["usual_action"] == "schedule follow-up testing"
    assert hit["topic_actions"] == [{"action": "schedule follow-up testing", "weight": 1}]


def test_kuzu_hit_action_contract_matches_inmemory_when_available(tmp_path: Path) -> None:
    pytest.importorskip("kuzu")
    from drchrono_mcp.inbox.graph.kuzu_store import KuzuGraphStore

    store = KuzuGraphStore(tmp_path / "voice_graph.kuzu")
    try:
        store.add_message(
            message_id="normal-no-action",
            subject="Normal shared topic",
            body="Everything looks reassuring.",
            facts=ResponseFacts(
                topic="shared_topic",
                normalcy="normal",
                phrase_key="shared_topic:normal",
            ),
            embedding=[1.0, 0.0],
        )
        store.add_message(
            message_id="abnormal-with-action",
            subject="Abnormal shared topic",
            body="Please schedule follow-up testing.",
            facts=ResponseFacts(
                topic="shared_topic",
                normalcy="abnormal",
                action="schedule follow-up testing",
                phrase_key="shared_topic:abnormal",
            ),
            embedding=[0.0, 1.0],
        )

        hit = store.query([1.0, 0.0], top_k=1)[0]

        assert hit["action"] is None
        assert hit["usual_action"] == "schedule follow-up testing"
        assert hit["topic_actions"] == [{"action": "schedule follow-up testing", "weight": 1}]
    finally:
        store.close()


def test_inmemory_persistence_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "voice_graph.memgraph.json"
    store = InMemoryGraphStore(path)
    _ingest(store, n=10)
    store.close()
    assert path.exists()

    reopened = InMemoryGraphStore(path)
    hits = reopened.query(HashingEmbedder().embed([_INCOMING])[0], top_k=1)
    assert hits and hits[0]["topic"] == "gestational_glucose"
