"""Ingest the message corpus into the typed response graph.

For each ``SentMessage``: extract ``ResponseFacts`` (heuristic), embed subject+body (local model),
and upsert into the ``GraphStore``. Backend-agnostic -- works against Kuzu or the in-memory store.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from drchrono_mcp.inbox.corpus.models import SentMessage
from drchrono_mcp.inbox.interfaces import Embedder, Extractor, GraphStore


@dataclass
class IngestStats:
    messages: int = 0
    topics: int = 0
    phrases: int = 0
    actions: int = 0


class GraphIngestor:
    """Drives corpus -> response graph using a pluggable embedder, extractor, and store."""

    def __init__(self, store: GraphStore, embedder: Embedder, extractor: Extractor) -> None:
        self.store = store
        self.embedder = embedder
        self.extractor = extractor

    def ingest(self, messages: Iterable[SentMessage]) -> IngestStats:
        items = list(messages)
        embeddings = self.embedder.embed([f"{m.subject}\n{m.body}" for m in items])
        topics: set[str] = set()
        phrases: set[str] = set()
        actions: set[str] = set()
        for message, embedding in zip(items, embeddings, strict=True):
            facts = self.extractor.extract(message.subject, message.body)
            self.store.add_message(
                message_id=message.id,
                subject=message.subject,
                body=message.body,
                facts=facts,
                embedding=embedding,
            )
            topics.add(facts.topic)
            phrases.add(facts.phrase_key or f"{facts.topic}:{facts.normalcy}")
            if facts.action:
                actions.add(facts.action)
        return IngestStats(
            messages=len(items),
            topics=len(topics),
            phrases=len(phrases),
            actions=len(actions),
        )
