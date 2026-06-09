"""MCP tools that expose the voice-grounded inbox autopilot.

Registered on the foundation FastMCP server via ``register_inbox_tools(mcp)``. Self-contained so
the whole module can be cherry-picked upstream. Vendor/client/physician-agnostic by design: the
voice graph is per-corpus (no physician is hard-coded), the tools work in any MCP client or
headless loop, and the engine does *retrieval + structure* while the host model composes the final
patient-specific draft -- so no PHI is sent to a remote LLM from inside the tool.

Synthetic-first: every tool runs with zero live credentials. ``source="live"`` is gated on
DrChrono OAuth credentials and token state. Message bodies are PHI -- returned to the caller,
never logged.
"""

from __future__ import annotations

from typing import Any

from drchrono_mcp.inbox.config import InboxConfig
from drchrono_mcp.inbox.corpus import CorpusBuilder, CorpusStore

# Coarse confidence gate for auto-draftable vs. queue-for-review. The finer HITL policy and the
# deterministic abnormal-lab rules table live in the (deferred) retrieval rules layer.
_MIN_CONFIDENCE = 0.15


def _topic_label(hit: dict[str, Any]) -> str:
    return hit.get("problem") or str(hit.get("topic", "your results")).replace("_", " ")


def _assemble_draft(hit: dict[str, Any]) -> str:
    """A neutral, physician-agnostic draft skeleton grounded by the retrieved facts.

    Deliberately contains no patient-specific values copied from another patient's exemplar and no
    signature -- the host model personalizes it using ``voice_exemplars`` as the style anchor.
    """
    lines = ["Dear [patient],", "", "I hope you're doing well. Your recent results are back."]
    if hit.get("normalcy") == "abnormal":
        topic = _topic_label(hit)
        lines.append(f"There is one value we should follow up on regarding your {topic}.")
    else:
        lines.append("Everything looks reassuring.")
    if hit.get("action"):
        lines += ["", "Next Steps:", f"1. {hit['action']}."]
    lines += ["", "Please message me through the portal with any questions.", "", "Warm regards,"]
    return "\n".join(lines)


def _suggested_action(hit: dict[str, Any]) -> str | None:
    if hit.get("action"):
        return hit["action"]
    topic_actions = hit.get("topic_actions") or []
    if topic_actions:
        return topic_actions[0].get("action")
    return None


def _select_hit(hits: list[dict[str, Any]], incoming: Any) -> dict[str, Any]:
    """Prefer explicit incoming-topic evidence over a generic vector neighbor."""
    if incoming.topic == "general":
        return hits[0]
    topic_hits = [hit for hit in hits if hit.get("topic") == incoming.topic]
    if not topic_hits:
        return hits[0]
    if incoming.normalcy != "unknown":
        for hit in topic_hits:
            if hit.get("normalcy") == incoming.normalcy:
                return hit
    return topic_hits[0]


def _exemplar_hits(
    hits: list[dict[str, Any]],
    selected: dict[str, Any],
    top_k: int,
) -> list[dict[str, Any]]:
    selected_id = selected.get("message_id")
    same_topic = [
        hit for hit in hits
        if hit.get("message_id") != selected_id and hit.get("topic") == selected.get("topic")
    ]
    remainder = [
        hit for hit in hits
        if hit.get("message_id") != selected_id and hit not in same_topic
    ]
    return ([selected] + same_topic + remainder)[:top_k]


async def drchrono_inbox_status() -> dict:
    """Report whether a voice corpus and response graph are built and ready to draft from.

    Use this first to decide whether to call drchrono_inbox_build_voice_graph before drafting.
    """
    config = InboxConfig.from_env()
    corpus = CorpusStore(config.corpus_path)
    graph_ready = (
        config.graph_path.exists() or config.graph_path.with_suffix(".memgraph.json").exists()
    )
    return {
        "source": config.source,
        "data_dir": str(config.data_dir),
        "corpus_ready": config.corpus_path.exists(),
        "corpus_count": corpus.count(),
        "graph_ready": graph_ready,
        "embedder_model": config.embedder_model,
    }


async def drchrono_inbox_build_voice_graph(
    source: str = "synthetic",
    n: int = 60,
    use_local_model: bool = False,
) -> dict:
    """Build (or rebuild) the physician's voice/response graph from their sent-message corpus.

    Ingests each sent message into a typed graph (Topic -> Phrase -> Action) so later drafts are
    grounded in the physician's own wording and usual next orders. Safe to re-run -- it rebuilds
    from scratch.

    Args:
        source: "synthetic" (default, no credentials) or "live" (DrChrono pull; needs OAuth).
        n: Number of synthetic messages to generate when source="synthetic".
        use_local_model: Use the local sentence-transformers embedder instead of the dep-free
            hashing embedder. Higher quality; requires the optional model to be installed.
    """
    from drchrono_mcp.inbox.embed import build_embedder
    from drchrono_mcp.inbox.extract import HeuristicExtractor
    from drchrono_mcp.inbox.graph import GraphIngestor, build_graph_store, reset_graph_store

    config = InboxConfig.from_env()
    config.source = source
    config.ensure_dirs()

    if source == "live":
        import os

        from drchrono_mcp.auth.oauth import OAuthManager
        from drchrono_mcp.clients.rest_client import DrChronoClient

        client_id = os.getenv("DRCHRONO_CLIENT_ID")
        client_secret = os.getenv("DRCHRONO_CLIENT_SECRET")
        if not client_id or not client_secret:
            return {
                "error": "Env vars DRCHRONO_CLIENT_ID and DRCHRONO_CLIENT_SECRET are required.",
                "hint": "Use source='synthetic' for development.",
            }
        oauth = OAuthManager(
            client_id,
            client_secret,
            os.getenv("DRCHRONO_REDIRECT_URI", "http://localhost:8765/callback"),
            scopes=["messages:read", "messages:write", "patients:read"],
        )
        if not oauth.is_authenticated:
            return {
                "error": "Not authenticated with DrChrono. Run the OAuth browser flow first.",
                "hint": "Use source='synthetic' for development.",
            }
        drchrono = DrChronoClient(oauth)
        try:
            await CorpusBuilder(config, drchrono).build_live()
        except Exception as exc:
            return {"error": f"Live corpus pull failed: {exc}"}
        finally:
            await drchrono.close()
    else:
        CorpusBuilder(config).build_synthetic(n=n)

    messages = CorpusStore(config.corpus_path).load()

    reset_graph_store(config.graph_path)
    embedder = build_embedder(config.embedder_model if use_local_model else None)
    store = build_graph_store(config.graph_path)
    try:
        stats = GraphIngestor(store, embedder, HeuristicExtractor()).ingest(messages)
    finally:
        store.close()
    return {
        "built": True,
        "messages": stats.messages,
        "topics": stats.topics,
        "phrases": stats.phrases,
        "actions": stats.actions,
        "embedder": type(embedder).__name__,
        "store": type(store).__name__,
    }


async def drchrono_inbox_draft_reply(
    subject: str,
    body: str,
    top_k: int = 3,
    use_local_model: bool = False,
) -> dict:
    """Draft a reply to an inbox message, grounded in the physician's own voice and usual action.

    Retrieves the closest past messages from the voice graph and returns: the matched clinical
    topic, the physician's usual next action for it (weighted across their history), their own
    wording as style exemplars, a neutral draft skeleton, and whether the item is confident enough
    to auto-draft or should be queued for one-tap human review.

    The returned draft is intentionally a skeleton -- the host model should personalize it using
    the voice_exemplars so no PHI is sent to a remote model from inside this tool.

    Args:
        subject: Subject line of the incoming message / lab notification.
        body: Body text of the incoming message.
        top_k: How many voice exemplars to return.
        use_local_model: Must match how the graph was built (drchrono_inbox_build_voice_graph);
            mismatched embedders produce incompatible vectors.
    """
    from drchrono_mcp.inbox.embed import build_embedder
    from drchrono_mcp.inbox.extract import HeuristicExtractor
    from drchrono_mcp.inbox.graph import build_graph_store

    config = InboxConfig.from_env()
    if not (config.graph_path.exists() or config.graph_path.with_suffix(".memgraph.json").exists()):
        return {"error": "No voice graph yet. Run drchrono_inbox_build_voice_graph first."}

    incoming = HeuristicExtractor().extract(subject, body)
    embedder = build_embedder(config.embedder_model if use_local_model else None)
    store = build_graph_store(config.graph_path)
    try:
        hits = store.query(embedder.embed([f"{subject}\n{body}"])[0], top_k=max(250, top_k))
        if incoming.topic != "general" and hasattr(store, "query_topic"):
            normalcy = incoming.normalcy if incoming.normalcy != "unknown" else None
            topic_hits = store.query_topic(incoming.topic, normalcy=normalcy, top_k=max(6, top_k))
            seen = {hit.get("message_id") for hit in topic_hits}
            hits = topic_hits + [hit for hit in hits if hit.get("message_id") not in seen]
    finally:
        store.close()

    if not hits:
        return {"needs_review": True, "reason": "no voice match found", "matched": None}

    top = _select_hit(hits, incoming)
    matched_topic = top["topic"]
    matched_normalcy = (
        incoming.normalcy
        if incoming.topic == matched_topic and incoming.normalcy != "unknown"
        else top["normalcy"]
    )
    suggested_action = _suggested_action(top)
    draft_hit = {
        **top,
        "normalcy": matched_normalcy,
        "problem": (
            incoming.problem
            if incoming.topic == matched_topic and incoming.problem
            else top["problem"]
        ),
        "demographic": (
            incoming.demographic
            if incoming.topic == matched_topic and incoming.demographic
            else top["demographic"]
        ),
        "action": suggested_action,
    }
    topic_confident = incoming.topic != "general" and matched_topic == incoming.topic
    action_confident = bool(suggested_action)
    needs_review = not (
        topic_confident and action_confident and matched_normalcy != "unknown"
    ) and (matched_topic == "general" or top["score"] < _MIN_CONFIDENCE)
    exemplar_hits = _exemplar_hits(hits, top, top_k)
    return {
        "matched": {
            "topic": matched_topic,
            "normalcy": matched_normalcy,
            "problem": draft_hit["problem"],
            "demographic": draft_hit["demographic"],
            "score": top["score"],
        },
        "suggested_action": suggested_action,
        "action_support": top["topic_actions"],
        "voice_exemplars": [h["body"] for h in exemplar_hits],
        "draft": _assemble_draft(draft_hit),
        "needs_review": needs_review,
        "reason": "low confidence -- queue for review" if needs_review else "confident match",
    }


INBOX_TOOLS = (
    drchrono_inbox_status,
    drchrono_inbox_build_voice_graph,
    drchrono_inbox_draft_reply,
)


def register_inbox_tools(mcp: Any) -> None:
    """Register the inbox autopilot tools on a FastMCP server instance."""
    for tool in INBOX_TOOLS:
        mcp.tool()(tool)
