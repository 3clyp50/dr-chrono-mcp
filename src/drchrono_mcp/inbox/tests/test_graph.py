"""Response-graph retrieval must return the doctor's voice + next action for a new message."""

from __future__ import annotations

from pathlib import Path

from drchrono_mcp.inbox.corpus.synthetic import generate
from drchrono_mcp.inbox.embed import HashingEmbedder
from drchrono_mcp.inbox.extract import HeuristicExtractor
from drchrono_mcp.inbox.graph.ingest import GraphIngestor
from drchrono_mcp.inbox.graph.memory_store import InMemoryGraphStore

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


def test_inmemory_persistence_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "voice_graph.memgraph.json"
    store = InMemoryGraphStore(path)
    _ingest(store, n=10)
    store.close()
    assert path.exists()

    reopened = InMemoryGraphStore(path)
    hits = reopened.query(HashingEmbedder().embed([_INCOMING])[0], top_k=1)
    assert hits and hits[0]["topic"] == "gestational_glucose"
