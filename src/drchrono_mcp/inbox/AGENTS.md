# AGENTS.md - Clinical Inbox Autopilot (corpus / voice graph / retrieval)

> Parent: repository root [`AGENTS.md`](../../../AGENTS.md). Read it before editing.

## Purpose
The reusable core of the inbox autopilot: ingest the physician's historical sent messages into a
**typed response graph**, then retrieve his *voice* + likely *next action* to ground drafted
inbox replies. Every other inbox lane (labs, tasks, patient messages) consumes this.

## Ownership
New project IP. Additive to the foundation, reusing `auth.oauth` + `clients.rest_client`.
Keep it self-contained so it can be PR'd upstream as the foundation's inbox capability.

## Local Contracts
- **Synthetic-first.** Everything must run end-to-end on the synthetic corpus with **zero live
  creds**. Live data is gated behind a single `source="live"` switch and OAuth env/token state.
  Never block dev on live access.
- **PHI discipline.** Treat every message body as PHI. Local models only for embedding/extraction
  unless a BAA-covered endpoint is configured. Never log message bodies. Synthetic data carries a
  `synthetic: true` marker.
- **Pluggable seams** (Protocols in `interfaces.py`, never hard-wire a vendor) - all implemented:
  - `Embedder` -> `embed.HashingEmbedder` (dep-free, deterministic, the default) /
    `SentenceTransformerEmbedder` (optional local model). `build_embedder()` picks the best
    available and **never** falls back to a remote API (PHI must stay on-device).
  - `GraphStore` -> `graph.kuzu_store.KuzuGraphStore` (embedded Cypher, production default) /
    `graph.memory_store.InMemoryGraphStore` (dep-free dev/test default, JSON-persisted).
    `graph.build_graph_store()` selects Kuzu when importable, else in-memory. Both stores expose
    `query_topic()` so deterministic topic extraction can anchor retrieval when vector ranking is
    swamped by a large generic-message cluster.
  - `Extractor` -> `extract.HeuristicExtractor` (keyword/regex first pass; LLM enrich later, BAA-only).
- **Response-graph schema** (the improvement over flat RAG):
  - Nodes: `Topic` (lab type / subject), `Phrase` (dot-template / reusable wording),
    `Problem`, `Demographic`, `Action` (order/follow-up), `Message` (the source utterance).
  - Edges: `Topic -[REPLIED_WITH]-> Phrase`, `Phrase -[FOR]-> Problem|Demographic`,
    `Phrase -[THEN_ORDERS]-> Action`, `Message -[INSTANCE_OF]-> Phrase`.
  - Retrieval = vector match on `Message` -> multi-hop to `Phrase` + `Action`.
  - As realized in `graph/schema.py`: conceptual `FOR` = `FOR_PROBLEM` + `FOR_DEMOGRAPHIC` (each a
    simple typed pair); added `Message -[ABOUT]-> Topic` (the retrieval anchor); `REPLIED_WITH` and
    `THEN_ORDERS` carry a `weight` (observation count) so retrieval ranks his *usual* wording and
    *usual* next order, not a one-off.
- **Determinism split.** Abnormal-lab *action* should come from an explicit rules table
  (thresholds); the graph supplies *wording* only. Keep the two separable. The rules table is
  **deferred** - `draft_reply` currently sources the action from the graph's weighted `THEN_ORDERS`
  and gates uncertain items via `needs_review` for one-tap human approval.

## Structure
Built:
- `config.py` - `InboxConfig` (source live|synthetic, user filter, date range, paths, model id).
- `interfaces.py` - `Embedder` / `Extractor` / `GraphStore` Protocols + `ResponseFacts`.
- `corpus/` - `models.py` (`SentMessage`), `store.py` (JSONL), `synthetic.py` (physician-style
  generator with gold labels), `builder.py` (`build_synthetic` + `build_live` live pull).
- `embed.py` - `HashingEmbedder` (default) / `SentenceTransformerEmbedder` + `build_embedder()`.
- `extract.py` - `HeuristicExtractor` (topic + normalcy + next action from the doctor's wording).
- `graph/` - `schema.py` (typed DDL), `kuzu_store.py` (`KuzuGraphStore`), `memory_store.py`
  (`InMemoryGraphStore`, JSON-persisted), `ingest.py` (`GraphIngestor`: corpus -> graph),
  `__init__.build_graph_store()` (backend factory) + `reset_graph_store()` (clean rebuild, prevents
  weight double-counting).
- `mcp_tools.py` - the public surface: `register_inbox_tools(mcp)` registers three
  physician-agnostic / client-agnostic tools on the foundation FastMCP server:
  - `drchrono_inbox_status` - is a corpus + voice graph built and ready to draft from?
  - `drchrono_inbox_build_voice_graph` - build/rebuild the voice graph (`source="live"` gated on
    OAuth env/token state; safe to re-run via `reset_graph_store`).
  - `drchrono_inbox_draft_reply` - retrieve voice + usual action for an incoming message and return
    a **neutral draft skeleton** + voice exemplars + a `needs_review` HITL gate. PHI-safe: the tool
    does retrieval + structure; the host model composes the patient-specific draft (no PHI to a
    remote LLM from inside the tool). It extracts the incoming topic first, queries the graph by
    topic as a fallback to cosine retrieval, and then returns only the top requested exemplars.
- `tests/` - `test_extract.py`, `test_graph.py`, `test_mcp_tools.py` (synthetic, zero creds; 21
  passing). `test_mcp_tools` guards the rebuild double-count fix.
- `cli.py` - dev entrypoint: `synth` / `stats` / `show` / `build-graph` / `retrieve` / `build-live`.

Wired: `server.py` calls `register_inbox_tools(mcp)` so the tools ship with the foundation server.

Live pull:
- OAuth tokens are cached locally by the foundation auth layer. `source="live"` requires
  `DRCHRONO_CLIENT_ID` and `DRCHRONO_CLIENT_SECRET`, plus an authorized token with
  `messages:read`, `messages:write`, and `patients:read`.
- `build_live` uses `/api/patient_messages`, `doctor=<doctor_id>`, `page_size=100`, cursor
  pagination, and no `since` param. Set `DRCHRONO_DOCTOR_ID` if `/users/current` cannot infer the
  doctor id for the authorized account.
- The live pull has a 500-page / 50,000-row safety cap. Add a resumable cursor/cap override before
  using it for full-history production backfills.

Next:
- `retrieval.py` - abnormal-lab **rules table** (the determinism split: rules pick the clinical
  action deterministically, the graph picks the voice). **Deferred** per product call - the graph's
  weighted `THEN_ORDERS` supplies the usual action for now; the rules table hardens it later.
- Full-history live pull beyond 50k rows: add resumable cursor/cap override if production
  evaluation needs more than the current safety-capped corpus.

## Work Guidance
- Live corpus pull: use `DrChronoClient.get("/patient_messages", {"doctor": doctor_id,
  "page_size": 100})` and advance with the exact query params from `next`. Do not use `since`.
- DrChrono may return long `429 Retry-After` windows; respect them. Avoid repeated preflight
  probes and reuse an already-built local `.inbox_data` graph when possible.
- Add BAA endpoint config before any optional remote LLM enrichment over real PHI.

## Verification
- CLI smoke (no creds), end to end: `synth --n 60` -> `stats` -> `build-graph` -> `retrieve`.
  `retrieve` must ground the canonical incoming "gestational glucose 197 mg/dL" to
  `topic=gestational_glucose, normalcy=abnormal`, action "Schedule a 3-hour OGTT", in his voice.
- MCP tools (no creds): the three `drchrono_inbox_*` tools register on FastMCP and run on synthetic
  data. `test_mcp_tools.py` covers build -> status -> draft for the canonical case, the rebuild
  double-count guard, the no-graph error, and the gated `source="live"`.
- Tests: `uv run pytest src/drchrono_mcp/inbox` (21 passing). Dep-light variant (no `uv sync`):
  `PYTHONPATH=src uv run --no-project --with 'pydantic>=2' --with pytest pytest src/drchrono_mcp/inbox/tests`.
- Kuzu backend: install `kuzu` and re-run `build-graph`/`retrieve` - `build_graph_store` auto-selects
  it and output matches the in-memory store. (Dev default needs no native dep.)
- Lint: `uvx ruff check src/drchrono_mcp/inbox` (or the foundation's `uv run ruff check src/`).

## Child DOX Index
_None yet - leaf boundary. `corpus/` and `graph/` are documented here until either grows its own
durable rules._
