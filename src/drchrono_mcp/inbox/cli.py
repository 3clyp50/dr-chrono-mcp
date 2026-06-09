"""Dev CLI for the inbox corpus + voice graph. Synthetic mode runs with zero live credentials.

    uv run python -m drchrono_mcp.inbox.cli synth --n 60
    uv run python -m drchrono_mcp.inbox.cli stats
    uv run python -m drchrono_mcp.inbox.cli show --n 2
    uv run python -m drchrono_mcp.inbox.cli build-graph
    uv run python -m drchrono_mcp.inbox.cli retrieve
"""

from __future__ import annotations

import argparse
from collections import Counter

from drchrono_mcp.inbox.config import InboxConfig
from drchrono_mcp.inbox.corpus import CorpusBuilder, CorpusStore

# An *incoming* lab notification (not the doctor's reply) -- the canonical case to ground a draft.
_DEMO_QUERY = (
    "Lab result available for prenatal patient: "
    "Gestational glucose screening, 1-hour, result 197 mg/dL (cutoff < 140)."
)


def cmd_synth(args: argparse.Namespace) -> None:
    config = InboxConfig.from_env()
    count = CorpusBuilder(config).build_synthetic(n=args.n, seed=args.seed)
    print(f"Wrote {count} synthetic messages -> {config.corpus_path}")


def cmd_stats(args: argparse.Namespace) -> None:
    config = InboxConfig.from_env()
    messages = CorpusStore(config.corpus_path).load()
    if not messages:
        print(f"No corpus at {config.corpus_path}. Run: synth")
        return
    by_category = Counter(m.category for m in messages)
    by_normalcy = Counter(m.meta.get("gold", {}).get("normalcy", "unknown") for m in messages)
    print(f"Corpus: {len(messages)} messages at {config.corpus_path}")
    print(f"Synthetic: {sum(1 for m in messages if m.synthetic)}")
    print("By category:")
    for key, value in by_category.most_common():
        print(f"  {key:24s} {value}")
    print(f"By normalcy: {dict(by_normalcy)}")


def cmd_show(args: argparse.Namespace) -> None:
    config = InboxConfig.from_env()
    messages = CorpusStore(config.corpus_path).load()
    for message in messages[: args.n]:
        print("=" * 72)
        print(f"[{message.category}] {message.subject}  ({message.sent_at})")
        print(f"gold: {message.meta.get('gold', {})}")
        print("-" * 72)
        print(message.body)


def cmd_build_graph(args: argparse.Namespace) -> None:
    from drchrono_mcp.inbox.embed import build_embedder
    from drchrono_mcp.inbox.extract import HeuristicExtractor
    from drchrono_mcp.inbox.graph import GraphIngestor, build_graph_store, reset_graph_store

    config = InboxConfig.from_env()
    messages = CorpusStore(config.corpus_path).load()
    if not messages:
        print(f"No corpus at {config.corpus_path}. Run: synth")
        return
    config.ensure_dirs()
    reset_graph_store(config.graph_path)
    embedder = build_embedder(config.embedder_model if args.model else None)
    store = build_graph_store(config.graph_path)
    try:
        stats = GraphIngestor(store, embedder, HeuristicExtractor()).ingest(messages)
    finally:
        store.close()
    print(f"Ingested {stats.messages} messages into {type(store).__name__}")
    print(f"  topics={stats.topics} phrases={stats.phrases} actions={stats.actions}")
    print(f"  embedder={type(embedder).__name__} (dim={embedder.dim})")


def cmd_retrieve(args: argparse.Namespace) -> None:
    from drchrono_mcp.inbox.embed import build_embedder
    from drchrono_mcp.inbox.graph import build_graph_store

    config = InboxConfig.from_env()
    embedder = build_embedder(config.embedder_model if args.model else None)
    store = build_graph_store(config.graph_path)
    query = args.text or _DEMO_QUERY
    try:
        hits = store.query(embedder.embed([query])[0], top_k=args.top_k)
    finally:
        store.close()
    print(f"Query: {query}\n")
    if not hits:
        print("No graph yet. Run: build-graph")
        return
    for rank, hit in enumerate(hits, 1):
        print(f"#{rank}  score={hit['score']}  topic={hit['topic']}  normalcy={hit['normalcy']}")
        print(f"    usual action: {hit['action']}")
        if hit.get("topic_actions"):
            actions = ", ".join(f"{a['action']} (x{a['weight']})" for a in hit["topic_actions"])
            print(f"    actions for topic: {actions}")
        print(f"    voice exemplar: {hit['body'][:280].replace(chr(10), ' ')}\n")


def cmd_build_live(args: argparse.Namespace) -> None:
    import asyncio
    import json

    from drchrono_mcp.inbox.mcp_tools import drchrono_inbox_build_voice_graph

    result = asyncio.run(
        drchrono_inbox_build_voice_graph(
            source="live",
            use_local_model=args.model,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="inbox", description="Clinical inbox corpus tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_synth = sub.add_parser("synth", help="generate the synthetic corpus")
    p_synth.add_argument("--n", type=int, default=60)
    p_synth.add_argument("--seed", type=int, default=7)
    p_synth.set_defaults(func=cmd_synth)

    sub.add_parser("stats", help="summarize the stored corpus").set_defaults(func=cmd_stats)

    p_show = sub.add_parser("show", help="print the first N messages")
    p_show.add_argument("--n", type=int, default=3)
    p_show.set_defaults(func=cmd_show)

    p_graph = sub.add_parser("build-graph", help="ingest the corpus into the voice graph")
    p_graph.add_argument("--model", action="store_true", help="use the local ST model, not hashing")
    p_graph.set_defaults(func=cmd_build_graph)

    p_retrieve = sub.add_parser("retrieve", help="retrieve voice + next action for a message")
    p_retrieve.add_argument("--text", help="incoming message text (default: gestational glucose)")
    p_retrieve.add_argument("--top-k", type=int, default=3)
    p_retrieve.add_argument("--model", action="store_true", help="use the local ST model")
    p_retrieve.set_defaults(func=cmd_retrieve)

    p_live = sub.add_parser("build-live", help="pull live DrChrono messages and build graph")
    p_live.add_argument("--model", action="store_true", help="use the local ST model")
    p_live.set_defaults(func=cmd_build_live)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
