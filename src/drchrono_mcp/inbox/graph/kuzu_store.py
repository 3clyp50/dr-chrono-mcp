"""Embedded-Kuzu response-graph store (the production default per the inbox AGENTS.md).

Holds the typed graph (Topic/Phrase/Problem/Demographic/Action/Message + edges from
``schema.py``). ``REPLIED_WITH``/``THEN_ORDERS`` weights are incremented per observation so
retrieval can surface the doctor's *usual* wording and next order. Embeddings are stored as JSON
strings and ranked with Python cosine at dev-corpus scale; swap to Kuzu's vector index when the
live corpus grows. Selected by the factory only when ``kuzu`` is importable -- otherwise the
in-memory store is used (see ``graph/__init__.py``).
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from drchrono_mcp.inbox.graph.schema import ddl_statements
from drchrono_mcp.inbox.interfaces import ResponseFacts


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class KuzuGraphStore:
    """``GraphStore`` backed by an embedded Kuzu database at ``path``."""

    def __init__(self, path: Path | str) -> None:
        import kuzu

        self._db = kuzu.Database(str(path))
        self._conn = kuzu.Connection(self._db)
        for statement in ddl_statements():
            self._conn.execute(statement)

    def _run(self, statement: str, params: dict[str, Any] | None = None) -> Any:
        return self._conn.execute(statement, parameters=params or {})

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
        self._run(
            "MERGE (m:Message {id: $id}) "
            "SET m.subject = $subject, m.body = $body, m.embedding = $emb",
            {"id": message_id, "subject": subject, "body": body,
             "emb": json.dumps(embedding or [])},
        )
        self._run("MERGE (t:Topic {key: $key}) SET t.label = $key", {"key": topic})
        self._run(
            "MERGE (p:Phrase {key: $key}) SET p.normalcy = $normalcy, p.exemplar = $exemplar",
            {"key": phrase_key, "normalcy": facts.normalcy, "exemplar": body},
        )
        self._run(
            "MATCH (m:Message {id: $id}), (t:Topic {key: $topic}) MERGE (m)-[:ABOUT]->(t)",
            {"id": message_id, "topic": topic},
        )
        self._run(
            "MATCH (m:Message {id: $id}), (p:Phrase {key: $phrase}) "
            "MERGE (m)-[:INSTANCE_OF]->(p)",
            {"id": message_id, "phrase": phrase_key},
        )
        self._run(
            "MATCH (t:Topic {key: $topic}), (p:Phrase {key: $phrase}) "
            "MERGE (t)-[r:REPLIED_WITH]->(p) SET r.weight = coalesce(r.weight, 0) + 1",
            {"topic": topic, "phrase": phrase_key},
        )
        if facts.action:
            self._run("MERGE (:Action {text: $text})", {"text": facts.action})
            self._run(
                "MATCH (p:Phrase {key: $phrase}), (a:Action {text: $text}) "
                "MERGE (p)-[r:THEN_ORDERS]->(a) SET r.weight = coalesce(r.weight, 0) + 1",
                {"phrase": phrase_key, "text": facts.action},
            )
        if facts.problem:
            self._run("MERGE (:Problem {name: $name})", {"name": facts.problem})
            self._run(
                "MATCH (p:Phrase {key: $phrase}), (x:Problem {name: $name}) "
                "MERGE (p)-[:FOR_PROBLEM]->(x)",
                {"phrase": phrase_key, "name": facts.problem},
            )
        if facts.demographic:
            self._run("MERGE (:Demographic {name: $name})", {"name": facts.demographic})
            self._run(
                "MATCH (p:Phrase {key: $phrase}), (x:Demographic {name: $name}) "
                "MERGE (p)-[:FOR_DEMOGRAPHIC]->(x)",
                {"phrase": phrase_key, "name": facts.demographic},
            )

    def query(self, query_embedding: list[float], top_k: int = 6) -> list[dict[str, Any]]:
        result = self._run("MATCH (m:Message) RETURN m.id, m.embedding")
        scored: list[tuple[float, str]] = []
        while result.has_next():
            mid, emb_json = result.get_next()
            scored.append((_cosine(query_embedding, json.loads(emb_json or "[]")), mid))
        scored.sort(key=lambda t: t[0], reverse=True)
        topic_actions_cache: dict[str, list[dict[str, Any]]] = {}
        top_phrase_cache: dict[str, str | None] = {}
        phrase_action_cache: dict[str, str | None] = {}
        return [
            self._expand(
                score,
                mid,
                topic_actions_cache=topic_actions_cache,
                top_phrase_cache=top_phrase_cache,
                phrase_action_cache=phrase_action_cache,
            )
            for score, mid in scored[:top_k]
        ]

    def query_topic(
        self,
        topic: str,
        normalcy: str | None = None,
        top_k: int = 6,
    ) -> list[dict[str, Any]]:
        rows = self._topic_rows(topic, normalcy, top_k)
        if not rows and normalcy is not None:
            rows = self._topic_rows(topic, None, top_k)
        topic_actions_cache: dict[str, list[dict[str, Any]]] = {}
        top_phrase_cache: dict[str, str | None] = {}
        phrase_action_cache: dict[str, str | None] = {}
        return [
            self._expand(
                1.0,
                mid,
                topic_actions_cache=topic_actions_cache,
                top_phrase_cache=top_phrase_cache,
                phrase_action_cache=phrase_action_cache,
            )
            for mid in rows
        ]

    def close(self) -> None:
        self._conn = None
        self._db = None

    # -- multi-hop expansion (per top-ranked message) ------------------------
    def _expand(
        self,
        score: float,
        message_id: str,
        *,
        topic_actions_cache: dict[str, list[dict[str, Any]]] | None = None,
        top_phrase_cache: dict[str, str | None] | None = None,
        phrase_action_cache: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        row = self._one(
            "MATCH (m:Message {id: $id})-[:INSTANCE_OF]->(p:Phrase) "
            "OPTIONAL MATCH (m)-[:ABOUT]->(t:Topic) "
            "OPTIONAL MATCH (p)-[:FOR_PROBLEM]->(pr:Problem) "
            "OPTIONAL MATCH (p)-[:FOR_DEMOGRAPHIC]->(d:Demographic) "
            "RETURN m.subject, m.body, p.key, p.normalcy, t.key, pr.name, d.name",
            {"id": message_id},
        )
        subject, body, phrase_key, normalcy, topic, problem, demographic = (
            row if row else ("", "", None, "unknown", None, None, None)
        )
        actions = (
            self._cached_topic_actions(topic, topic_actions_cache)
            if topic
            else []
        )
        phrase_action = (
            self._cached_phrase_action(phrase_key, phrase_action_cache)
            if phrase_key
            else None
        )
        usual_phrase = (
            self._cached_top_phrase(topic, top_phrase_cache)
            if topic
            else None
        )
        return {
            "score": round(score, 4),
            "message_id": message_id,
            "subject": subject,
            "body": body,
            "topic": topic,
            "phrase_key": phrase_key,
            "normalcy": normalcy,
            "problem": problem,
            "demographic": demographic,
            "action": phrase_action,
            "usual_action": actions[0]["action"] if actions else None,
            "usual_phrase": usual_phrase,
            "topic_actions": actions,
        }

    def _one(self, statement: str, params: dict[str, Any]) -> list[Any] | None:
        result = self._run(statement, params)
        return result.get_next() if result.has_next() else None

    def _topic_rows(
        self,
        topic: str,
        normalcy: str | None,
        top_k: int,
    ) -> list[str]:
        if normalcy is None:
            result = self._run(
                "MATCH (m:Message)-[:ABOUT]->(t:Topic {key: $topic}) "
                "MATCH (m)-[:INSTANCE_OF]->(p:Phrase) "
                "OPTIONAL MATCH (p)-[:THEN_ORDERS]->(a:Action) "
                "RETURN m.id, count(a) AS action_count "
                "ORDER BY action_count DESC LIMIT $limit",
                {"topic": topic, "limit": top_k},
            )
        else:
            result = self._run(
                "MATCH (m:Message)-[:ABOUT]->(t:Topic {key: $topic}) "
                "MATCH (m)-[:INSTANCE_OF]->(p:Phrase) "
                "WHERE p.normalcy = $normalcy "
                "OPTIONAL MATCH (p)-[:THEN_ORDERS]->(a:Action) "
                "RETURN m.id, count(a) AS action_count "
                "ORDER BY action_count DESC LIMIT $limit",
                {"topic": topic, "normalcy": normalcy, "limit": top_k},
            )
        rows: list[str] = []
        while result.has_next():
            rows.append(result.get_next()[0])
        return rows

    def _top_phrase(self, topic: str) -> str | None:
        row = self._one(
            "MATCH (t:Topic {key: $topic})-[r:REPLIED_WITH]->(p:Phrase) "
            "RETURN p.key ORDER BY r.weight DESC LIMIT 1",
            {"topic": topic},
        )
        return row[0] if row else None

    def _cached_top_phrase(
        self,
        topic: str,
        cache: dict[str, str | None] | None,
    ) -> str | None:
        if cache is None:
            return self._top_phrase(topic)
        if topic not in cache:
            cache[topic] = self._top_phrase(topic)
        return cache[topic]

    def _phrase_action(self, phrase_key: str) -> str | None:
        row = self._one(
            "MATCH (p:Phrase {key: $phrase})-[r:THEN_ORDERS]->(a:Action) "
            "RETURN a.text ORDER BY r.weight DESC LIMIT 1",
            {"phrase": phrase_key},
        )
        return row[0] if row else None

    def _cached_phrase_action(
        self,
        phrase_key: str,
        cache: dict[str, str | None] | None,
    ) -> str | None:
        if cache is None:
            return self._phrase_action(phrase_key)
        if phrase_key not in cache:
            cache[phrase_key] = self._phrase_action(phrase_key)
        return cache[phrase_key]

    def _topic_actions(self, topic: str) -> list[dict[str, Any]]:
        result = self._run(
            "MATCH (t:Topic {key: $topic})-[:REPLIED_WITH]->(:Phrase)-[r:THEN_ORDERS]->(a:Action) "
            "RETURN a.text, sum(r.weight) AS w ORDER BY w DESC",
            {"topic": topic},
        )
        tally: Counter = Counter()
        while result.has_next():
            text, weight = result.get_next()
            tally[text] += int(weight)
        return [{"action": a, "weight": w} for a, w in tally.most_common()]

    def _cached_topic_actions(
        self,
        topic: str,
        cache: dict[str, list[dict[str, Any]]] | None,
    ) -> list[dict[str, Any]]:
        if cache is None:
            return self._topic_actions(topic)
        if topic not in cache:
            cache[topic] = self._topic_actions(topic)
        return cache[topic]
