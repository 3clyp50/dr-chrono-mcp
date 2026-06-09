"""Pluggable seams for the inbox autopilot.

Never hard-wire a vendor: embedding, extraction, and graph storage are swapped through these
Protocols (see the inbox AGENTS.md). ``ResponseFacts`` is the structured signal the response graph
is built from.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True)
class ResponseFacts:
    """Structured facts extracted from one sent message."""

    topic: str  # lab type / subject, normalized (graph anchor)
    normalcy: str = "unknown"  # "normal" | "abnormal" | "unknown"
    problem: str | None = None  # condition context
    demographic: str | None = None  # e.g. "prenatal", "pediatric"
    action: str | None = None  # next order / follow-up the doctor took
    phrase_key: str | None = None  # cluster id for reusable wording


@runtime_checkable
class Embedder(Protocol):
    """Turns text into vectors. Local model by default (PHI must not leave without a BAA)."""

    dim: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@runtime_checkable
class Extractor(Protocol):
    """Derives ``ResponseFacts`` from a message. Heuristic first; optional LLM enrichment."""

    def extract(self, subject: str, body: str) -> ResponseFacts: ...


@runtime_checkable
class GraphStore(Protocol):
    """Typed response-graph store. Default impl is embedded Kuzu."""

    def add_message(
        self,
        *,
        message_id: str,
        subject: str,
        body: str,
        facts: ResponseFacts,
        embedding: list[float] | None,
    ) -> None: ...

    def query(self, query_embedding: list[float], top_k: int = 6) -> list[dict[str, Any]]: ...

    def query_topic(
        self,
        topic: str,
        normalcy: str | None = None,
        top_k: int = 6,
    ) -> list[dict[str, Any]]: ...

    def close(self) -> None: ...
