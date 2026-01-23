# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DrChrono MCP Server - A Python MCP (Model Context Protocol) server for the DrChrono healthcare API. Provides tools for patient management, appointments, clinical notes, billing, FHIR R4 interoperability, and persistent clinical memory via SimpleMem.

## Commands

```bash
# Install dependencies
uv sync

# Run server (stdio transport for local MCP clients like Claude Desktop)
uv run drchrono-mcp

# Run server (Streamable HTTP transport - recommended for remote clients)
uv run drchrono-mcp --http
# Endpoint: http://127.0.0.1:8000/mcp

# Run with custom host/port
uv run drchrono-mcp --http --host 0.0.0.0 --port 8080

# Run server (SSE transport - deprecated, use --http instead)
uv run drchrono-mcp --sse --port 8080

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## Architecture

```
server.py (FastMCP entry point)
    ├── Lazy-initialized singletons:
    │   ├── OAuthManager → handles OAuth 2.0 flow, token refresh
    │   ├── DrChronoClient → REST API with rate limiting
    │   ├── FHIRClient → FHIR R4 via ConnectEHR (optional)
    │   └── SimpleMemClient → persistent clinical memory (optional)
    │
    └── MCP Tools (registered via @mcp.tool() decorator)
```

### Key Components

- **`server.py`**: All MCP tools are defined inline using FastMCP decorators. Tools call lazy-initialized clients.
- **`auth/oauth.py`**: OAuth 2.0 Authorization Code flow with local callback server. Handles token exchange and refresh.
- **`auth/token_store.py`**: Secure token persistence to `~/.drchrono/tokens.json` (mode 600).
- **`clients/rest_client.py`**: Async HTTP client with automatic 429 rate limit handling (exponential backoff) and bulk API support.
- **`clients/fhir_client.py`**: FHIR R4 client for ConnectEHR integration. Requires separate FHIR credentials.
- **`models/types.py`**: Pydantic models and Literal types (prevents LLM hallucination on constrained parameters).

### Transport Modes

- **stdio** (default): For MCP clients that spawn the server as a subprocess (e.g., Claude Desktop)
- **streamable-http** (`--http`): Recommended HTTP transport for remote clients. Uses `mcp.streamable_http_app()` served by uvicorn. Endpoint at `/mcp`.
- **sse** (`--sse`): Deprecated HTTP transport. Uses `mcp.sse_app()`. Endpoint at `/sse`.

### MCP-UI Visualization Tools

The server includes MCP-UI powered visualization tools that return interactive HTML content:

- **`drchrono_visualize_labs`**: Chart.js line chart of lab results over time
- **`drchrono_visualize_patient_dashboard`**: Clinical summary card with allergies, medications, problems

These tools return `{ "content": [resource] }` format where `resource` is an MCP-UI resource object. Clients supporting MCP-UI (like Agent Zero with the MCP-UI renderer) will display interactive visualizations.

### DrChrono API Details

- REST Base: `https://app.drchrono.com/api/`
- OAuth Authorize: `https://app.drchrono.com/o/authorize/`
- OAuth Token: `https://app.drchrono.com/o/token/`
- Bulk APIs: POST to `/{resource}_list` to start async job, poll with `uuid` parameter
- Max page size: 250 (standard), 1000 (bulk APIs)

## Environment Variables

Required:
- `DRCHRONO_CLIENT_ID` - OAuth client ID
- `DRCHRONO_CLIENT_SECRET` - OAuth client secret

Optional:
- `DRCHRONO_REDIRECT_URI` - OAuth callback (default: `http://localhost:8765/callback`)
- `DRCHRONO_TOKEN_FILE` - Custom token storage path
- `DRCHRONO_FHIR_BASE_URL` - FHIR server URL for ConnectEHR
- `DRCHRONO_FHIR_CLIENT_ID` / `DRCHRONO_FHIR_CLIENT_SECRET` - FHIR credentials
- `SIMPLEMEM_API_URL` / `SIMPLEMEM_ACCESS_TOKEN` - Memory service credentials

## Code Style

- Python 3.11+ with type hints
- Line length: 100 characters
- Ruff for linting (E, F, I, UP, B rules) and formatting
- All MCP tools prefixed with `drchrono_`
- Async/await throughout (httpx AsyncClient)
