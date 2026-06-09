# AGENTS.md - dr-chrono-mcp (Foundation MCP Server)

## Purpose
The Python/FastMCP server for the DrChrono API and the spine of this project. Provides OAuth2,
a rate-limited REST client, a FHIR R4 client, persistent clinical memory (SimpleMem), curated
`drchrono_` tools, and MCP-UI visualizations. We **extend** it with the clinical-inbox autopilot.

## Ownership
Owned by the DrChrono MCP maintainers. New inbox work is additive. Do not gratuitously rewrite
foundation modules; prefer additive modules under `src/drchrono_mcp/inbox/`.

## Local Contracts
- **Reuse, don't reinvent:** all DrChrono HTTP goes through `clients/rest_client.py`
  (`DrChronoClient`: `get/post/patch/delete`, `get_paginated`, `bulk_request`). Auth + refresh
  via `auth/oauth.py` (`OAuthManager`); tokens persisted by `auth/token_store.py` (mode 600).
- **Tool conventions:** all MCP tools prefixed `drchrono_`; outcomes over raw responses; flat
  args; `Literal`s for enums (`models/types.py`) to prevent hallucinated params; rich docstrings.
- **Transports:** stdio (default), `--http` streamable-HTTP at `/mcp` (recommended remote),
  `--sse` (deprecated).
- **Style:** Python 3.11+, async throughout, `ruff` (E,F,I,UP,B), line length 100.
- Detailed architecture notes live in [`CLAUDE.md`](CLAUDE.md). Keep it and this file consistent.

## Structure map
- `server.py` - FastMCP entry; lazy singletons (OAuthManager, DrChronoClient, FHIRClient, SimpleMemClient); tool registration.
- `auth/` - `oauth.py` (auth-code flow + refresh, local callback), `token_store.py`.
- `clients/` - `rest_client.py` (REST + bulk), `fhir_client.py` (ConnectEHR R4), `simplemem_client.py` (memory).
- `tools/` - `clinical.py`, `clinical_context.py` (`drchrono_get_clinical_context` aggregator), `billing.py`, `lab_imaging.py`, `fhir.py`, `auth_tools.py`.
- `ui/` - MCP-UI builders (`clinical_charts.py`, `clinical_display.py`).
- `models/types.py` - Pydantic models + Literals.
- `inbox/` - **new**: clinical-inbox autopilot (corpus, voice graph, retrieval). Its
  `mcp_tools.register_inbox_tools(mcp)` is called from `server.py`, so three `drchrono_inbox_*`
  tools ship with the server (they run synthetic-first, no creds). See its AGENTS.md.

## Work Guidance
- Inbox tools are registered via `inbox.mcp_tools.register_inbox_tools(mcp)` in `server.py`; add
  new inbox tools to that registrar, backed by `inbox/` modules. Note: `server.py` resolves OAuth
  env at import time, so the server only *boots* with creds, but the inbox tool bodies run on the
  synthetic corpus without them, and the tests import `inbox.mcp_tools` directly (never `server`).
- Reuse `DrChronoClient` for all DrChrono REST calls (`/patient_messages`, `/api/messages`,
  `/api/tasks`, labs, etc.).
- Live sent-message corpus pulls use cursor pagination on `/patient_messages` with
  `doctor=<doctor_id>` and `page_size=100`; do not use `since` on that endpoint. Other large
  resources may still use `DrChronoClient.bulk_request(...)` when the API supports it.

## Verification
- Lint: `uv run ruff check src/` - Format: `uv run ruff format src/`
- Run: `uv run drchrono-mcp` (stdio) or `uv run drchrono-mcp --http` (endpoint `/mcp`).
- Requires `DRCHRONO_CLIENT_ID` / `DRCHRONO_CLIENT_SECRET` for any live call (see `.env.example`).

## Child DOX Index
- [`src/drchrono_mcp/inbox/AGENTS.md`](src/drchrono_mcp/inbox/AGENTS.md) - clinical-inbox autopilot:
  message corpus builder, doctor voice/response graph, voice-grounded retrieval.
