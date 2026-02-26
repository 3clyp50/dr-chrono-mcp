# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DrChrono MCP Server - A Python MCP (Model Context Protocol) server for the DrChrono healthcare API. Provides tools for patient management, appointments, clinical notes, billing, FHIR R4 interoperability, persistent clinical memory via SimpleMem, and MCP-UI powered clinical visualizations.

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

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## Architecture

```
server.py (FastMCP entry point)
 ├── Lazy-initialized singletons:
 │ ├── OAuthManager → handles OAuth 2.0 flow, token refresh
 │ ├── DrChronoClient → REST API with rate limiting
 │ ├── FHIRClient → FHIR R4 via ConnectEHR (optional)
 │ └── SimpleMemClient → persistent clinical memory (optional)
 │
 └── MCP Tools (registered via @mcp.tool() decorator)
      ├── Auth tools (status, start, exchange, logout)
      ├── Clinical tools (patients, appointments, meds, allergies, problems, labs, notes)
      ├── Clinical context (unified patient summary)
      ├── Memory tools (store/search encounter history)
      └── Visualization tools (MCP-UI powered HTML dashboards)
```

### Key Components

- **`server.py`**: All MCP tools defined inline using FastMCP decorators. No web framework, no routes.
- **`auth/oauth.py`**: OAuth 2.0 Authorization Code flow with local callback server.
- **`auth/token_store.py`**: Secure token persistence to `~/.drchrono/tokens.json` (mode 600).
- **`clients/rest_client.py`**: Async HTTP client with automatic 429 rate limit handling.
- **`clients/fhir_client.py`**: FHIR R4 client for ConnectEHR integration (optional).
- **`ui/theme/`**: Design tokens (zinc palette, teal accent), base CSS, SVG icons.
- **`ui/components/`**: Reusable clinical UI components (PatientHeader, AllergyList, MedicationList, LabPanel, ClinicalCard, etc.)
- **`ui/clinical_charts.py`**: Chart.js visualization builder for lab trends.
- **`ui/clinical_display.py`**: HTML assembly for clinical displays.

### Transport Modes

- **stdio** (default): For MCP clients that spawn the server as a subprocess
- **streamable-http** (`--http`): HTTP transport for remote clients. Served by uvicorn at `/mcp`.

### Design System

The UI uses a professional, restrained clinical aesthetic:
- Zinc-based neutral palette (no purple, pink, or decorative gradients)
- Single teal accent (#14b8a6 dark, #0d9488 light) for interactive elements
- Clinical severity colors used only where medically meaningful (red=critical, amber=warning, green=normal)
- Inter for body text, JetBrains Mono for clinical values
- No glows, no decorative animations, no serif display fonts

### MCP-UI Visualization Tools

Tools return `{ "content": [resource] }` where resource is an MCP-UI HTML resource:

- **`drchrono_visualize_labs`**: Chart.js line chart of lab results over time
- **`drchrono_visualize_patient_dashboard`**: Clinical summary with allergies, medications, problems

These render as interactive HTML in any MCP-UI compatible client.

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
