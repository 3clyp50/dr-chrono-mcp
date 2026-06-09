"""Response-graph schema (the improvement over flat RAG).

Conceptual model (see the inbox AGENTS.md):
    Topic   -[REPLIED_WITH]->  Phrase
    Phrase  -[FOR]->           Problem | Demographic
    Phrase  -[THEN_ORDERS]->   Action
    Message -[INSTANCE_OF]->   Phrase
    Message -[ABOUT]->         Topic     (retrieval anchor)

The conceptual ``FOR`` edge is realized as two typed relations (``FOR_PROBLEM`` /
``FOR_DEMOGRAPHIC``) so each stays a simple typed pair -- portable across Kuzu versions and the
in-memory store alike. ``REPLIED_WITH`` and ``THEN_ORDERS`` carry a ``weight`` (observation count)
so retrieval can rank the doctor's *usual* wording and *usual* next order for a topic.
"""

from __future__ import annotations

NODE_LABELS: tuple[str, ...] = (
    "Topic", "Phrase", "Problem", "Demographic", "Action", "Message",
)

REL_TYPES: tuple[str, ...] = (
    "REPLIED_WITH", "FOR_PROBLEM", "FOR_DEMOGRAPHIC", "THEN_ORDERS", "INSTANCE_OF", "ABOUT",
)

# Embeddings are stored as JSON strings (portable, version-robust); cosine is done in Python over
# the dev-scale corpus. Swap to a native vector index when the live corpus grows.
_NODE_DDL: tuple[str, ...] = (
    "CREATE NODE TABLE IF NOT EXISTS Topic(key STRING, label STRING, embedding STRING,"
    " PRIMARY KEY(key))",
    "CREATE NODE TABLE IF NOT EXISTS Phrase(key STRING, normalcy STRING, exemplar STRING,"
    " PRIMARY KEY(key))",
    "CREATE NODE TABLE IF NOT EXISTS Problem(name STRING, PRIMARY KEY(name))",
    "CREATE NODE TABLE IF NOT EXISTS Demographic(name STRING, PRIMARY KEY(name))",
    "CREATE NODE TABLE IF NOT EXISTS Action(text STRING, PRIMARY KEY(text))",
    "CREATE NODE TABLE IF NOT EXISTS Message(id STRING, subject STRING, body STRING,"
    " sent_at STRING, embedding STRING, PRIMARY KEY(id))",
)

_REL_DDL: tuple[str, ...] = (
    "CREATE REL TABLE IF NOT EXISTS REPLIED_WITH(FROM Topic TO Phrase, weight INT64)",
    "CREATE REL TABLE IF NOT EXISTS FOR_PROBLEM(FROM Phrase TO Problem)",
    "CREATE REL TABLE IF NOT EXISTS FOR_DEMOGRAPHIC(FROM Phrase TO Demographic)",
    "CREATE REL TABLE IF NOT EXISTS THEN_ORDERS(FROM Phrase TO Action, weight INT64)",
    "CREATE REL TABLE IF NOT EXISTS INSTANCE_OF(FROM Message TO Phrase)",
    "CREATE REL TABLE IF NOT EXISTS ABOUT(FROM Message TO Topic)",
)


def ddl_statements() -> tuple[str, ...]:
    """All CREATE statements, node tables before relationship tables."""
    return _NODE_DDL + _REL_DDL
