"""Doctor voice/response graph (built on the message corpus).

Schema (see the inbox AGENTS.md): Topic -[REPLIED_WITH]-> Phrase -[FOR]-> Problem|Demographic,
Phrase -[THEN_ORDERS]-> Action, Message -[INSTANCE_OF]-> Phrase, Message -[ABOUT]-> Topic.
Retrieval = vector match on Message -> multi-hop to the usual Phrase + Action for the Topic.

``build_graph_store`` returns the production Kuzu store when ``kuzu`` is importable, else the
pure-Python in-memory store (the synthetic-first dev/test default). Both satisfy ``GraphStore``.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from drchrono_mcp.inbox.graph.ingest import GraphIngestor, IngestStats
from drchrono_mcp.inbox.graph.memory_store import InMemoryGraphStore
from drchrono_mcp.inbox.interfaces import GraphStore

__all__ = [
    "GraphIngestor",
    "IngestStats",
    "InMemoryGraphStore",
    "build_graph_store",
    "reset_graph_store",
]


def build_graph_store(graph_path: Path, *, prefer_kuzu: bool = True) -> GraphStore:
    """Pick the best available store: Kuzu if installed, else the in-memory JSON-backed store."""
    if prefer_kuzu:
        try:
            from drchrono_mcp.inbox.graph.kuzu_store import KuzuGraphStore

            return KuzuGraphStore(graph_path)
        except ImportError:
            pass
    return InMemoryGraphStore(graph_path.with_suffix(".memgraph.json"))


def reset_graph_store(graph_path: Path) -> None:
    """Delete existing graph artifacts so a rebuild starts clean.

    Ingest increments ``REPLIED_WITH`` / ``THEN_ORDERS`` weights, so re-ingesting into a kept store
    would double-count. Call this before any full rebuild. Covers both backends' on-disk forms.
    """
    graph_path.with_suffix(".memgraph.json").unlink(missing_ok=True)
    if graph_path.is_dir():
        shutil.rmtree(graph_path, ignore_errors=True)
    elif graph_path.exists():
        graph_path.unlink(missing_ok=True)
