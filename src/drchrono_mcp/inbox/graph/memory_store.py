"""Pure-Python response-graph store. No native deps -- the synthetic-first dev/test default.

Implements the same ``GraphStore`` Protocol as the Kuzu store, so code is identical whichever
backend the factory picks. Persists to JSON so the CLI can ``build-graph`` once and ``retrieve``
later. Cosine ranking is done in Python (fine at dev-corpus scale).
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from drchrono_mcp.inbox.interfaces import ResponseFacts


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class InMemoryGraphStore:
    """Typed response graph held in dicts; optional JSON persistence at ``path``."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else None
        self.messages: dict[str, dict[str, Any]] = {}
        self.topics: dict[str, str] = {}  # key -> human label
        self.phrases: dict[str, dict[str, str]] = {}  # key -> {normalcy, exemplar}
        self.replied_with: dict[str, Counter] = defaultdict(Counter)  # topic -> phrase -> weight
        self.then_orders: dict[str, Counter] = defaultdict(Counter)  # phrase -> action -> weight
        self.for_problem: dict[str, set[str]] = defaultdict(set)
        self.for_demographic: dict[str, set[str]] = defaultdict(set)
        if self.path and self.path.exists():
            self._load()

    # -- GraphStore Protocol -------------------------------------------------
    def add_message(
        self,
        *,
        message_id: str,
        subject: str,
        body: str,
        facts: ResponseFacts,
        embedding: list[float] | None,
    ) -> None:
        topic = facts.topic
        phrase_key = facts.phrase_key or f"{topic}:{facts.normalcy}"
        self.topics.setdefault(topic, topic)
        self.phrases.setdefault(phrase_key, {"normalcy": facts.normalcy, "exemplar": body})
        self.replied_with[topic][phrase_key] += 1
        if facts.action:
            self.then_orders[phrase_key][facts.action] += 1
        if facts.problem:
            self.for_problem[phrase_key].add(facts.problem)
        if facts.demographic:
            self.for_demographic[phrase_key].add(facts.demographic)
        self.messages[message_id] = {
            "subject": subject,
            "body": body,
            "embedding": embedding or [],
            "topic": topic,
            "phrase_key": phrase_key,
            "normalcy": facts.normalcy,
            "problem": facts.problem,
            "demographic": facts.demographic,
            "action": facts.action,
        }

    def query(self, query_embedding: list[float], top_k: int = 6) -> list[dict[str, Any]]:
        scored = (
            (_cosine(query_embedding, rec["embedding"]), mid, rec)
            for mid, rec in self.messages.items()
        )
        ranked = sorted(scored, key=lambda t: t[0], reverse=True)[:top_k]
        return [self._expand(score, mid, rec) for score, mid, rec in ranked]

    def query_topic(
        self,
        topic: str,
        normalcy: str | None = None,
        top_k: int = 6,
    ) -> list[dict[str, Any]]:
        candidates = [
            (mid, rec) for mid, rec in self.messages.items()
            if rec["topic"] == topic and (normalcy is None or rec["normalcy"] == normalcy)
        ]
        if not candidates and normalcy is not None:
            candidates = [
                (mid, rec) for mid, rec in self.messages.items()
                if rec["topic"] == topic
            ]
        ranked = sorted(
            candidates,
            key=lambda item: (
                bool(item[1]["action"]),
                item[1]["normalcy"] == normalcy,
                item[0],
            ),
            reverse=True,
        )[:top_k]
        return [self._expand(1.0, mid, rec) for mid, rec in ranked]

    def close(self) -> None:
        if self.path:
            self._save()

    # -- multi-hop expansion -------------------------------------------------
    def _expand(self, score: float, message_id: str, rec: dict[str, Any]) -> dict[str, Any]:
        topic = rec["topic"]
        phrase_key = rec["phrase_key"]
        topic_actions = self._topic_actions(topic)
        return {
            "score": round(score, 4),
            "message_id": message_id,
            "subject": rec["subject"],
            "body": rec["body"],
            "topic": topic,
            "phrase_key": phrase_key,
            "normalcy": rec["normalcy"],
            "problem": rec["problem"],
            "demographic": rec["demographic"],
            "action": rec["action"],
            "usual_action": topic_actions[0]["action"] if topic_actions else None,
            "usual_phrase": self._top_phrase(topic),
            "topic_actions": topic_actions,
        }

    def _top_phrase(self, topic: str) -> str | None:
        phrases = self.replied_with.get(topic)
        return phrases.most_common(1)[0][0] if phrases else None

    def _topic_actions(self, topic: str) -> list[dict[str, Any]]:
        """Actions the doctor orders for this topic, aggregated over its phrases, by frequency."""
        tally: Counter = Counter()
        for phrase_key in self.replied_with.get(topic, {}):
            tally.update(self.then_orders.get(phrase_key, {}))
        return [{"action": action, "weight": weight} for action, weight in tally.most_common()]

    # -- persistence ---------------------------------------------------------
    def _save(self) -> None:
        assert self.path is not None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "messages": self.messages,
            "topics": self.topics,
            "phrases": self.phrases,
            "replied_with": {t: dict(c) for t, c in self.replied_with.items()},
            "then_orders": {p: dict(c) for p, c in self.then_orders.items()},
            "for_problem": {p: sorted(s) for p, s in self.for_problem.items()},
            "for_demographic": {p: sorted(s) for p, s in self.for_demographic.items()},
        }
        self.path.write_text(json.dumps(payload), encoding="utf-8")

    def _load(self) -> None:
        assert self.path is not None
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.messages = data.get("messages", {})
        self.topics = data.get("topics", {})
        self.phrases = data.get("phrases", {})
        self.replied_with = defaultdict(Counter, {
            t: Counter(c) for t, c in data.get("replied_with", {}).items()
        })
        self.then_orders = defaultdict(Counter, {
            p: Counter(c) for p, c in data.get("then_orders", {}).items()
        })
        self.for_problem = defaultdict(set, {
            p: set(s) for p, s in data.get("for_problem", {}).items()
        })
        self.for_demographic = defaultdict(set, {
            p: set(s) for p, s in data.get("for_demographic", {}).items()
        })
