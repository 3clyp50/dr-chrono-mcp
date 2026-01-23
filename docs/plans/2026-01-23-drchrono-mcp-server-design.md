# DrChrono MCP Server Design

**Date:** 2026-01-23
**Status:** Approved for Implementation

## Overview

A Python-based MCP (Model Context Protocol) server for the DrChrono healthcare API, providing both REST API and FHIR R4 capabilities for clinical workflows, billing, and lab/imaging data access.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DrChrono MCP Server                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  OAuth Manager  │  │  Token Storage  │  │  Rate Limiter  │  │
│  │  (Auth Flow)    │  │  (Secure File)  │  │  (429 Handling)│  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
│           │                    │                   │            │
│  ┌────────▼────────────────────▼───────────────────▼────────┐  │
│  │                    API Client Layer                       │  │
│  │         (REST: app.drchrono.com/api/*)                   │  │
│  │         (FHIR: dynamicfhir.com R4 endpoints)             │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               │                                 │
│  ┌────────────────────────────▼─────────────────────────────┐  │
│  │                    MCP Tool Layer                         │  │
│  ├──────────────┬──────────────┬──────────────┬─────────────┤  │
│  │   Clinical   │   Billing    │  Lab/Imaging │    FHIR     │  │
│  │   (8 tools)  │   (3 tools)  │   (3 tools)  │  (3 tools)  │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Design Principles

Following MCP best practices:

1. **Outcomes over operations** - Tools return actionable results, not raw API responses
2. **Flat arguments** - Primitive types, Literals for enums, no nested dicts
3. **Instructions as context** - Rich docstrings explaining when/how to use each tool
4. **Curated ruthlessly** - 19 tools covering essential workflows
5. **Service-prefixed names** - All tools prefixed with `drchrono_`
6. **Paginated results** - `limit` parameters with metadata for large result sets

## Authentication

### OAuth 2.0 Authorization Code Flow

**Endpoints:**
- Authorization: `https://app.drchrono.com/o/authorize/`
- Token: `https://app.drchrono.com/o/token/`
- API Base: `https://app.drchrono.com/api/`

**Flow:**
1. User starts auth via `drchrono_auth_status` tool
2. Tool returns authorization URL to visit
3. User authorizes in browser, redirected to localhost callback
4. Server exchanges code for access/refresh tokens
5. Tokens persisted securely, auto-refreshed on expiry

**Scopes:**
- `calendar:read calendar:write` - Appointments
- `patients:read patients:write` - Patient data
- `clinical:read clinical:write` - Clinical notes, medications
- `billing:read` - Billing data
- `labs:read` - Lab results

### FHIR Authentication (ConnectEHR)

FHIR access requires separate ConnectEHR credentials configured at the practice level. The server will support both REST and FHIR auth when credentials are provided.

## Tool Specifications

### Auth Tool (1)

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `drchrono_auth_status` | Check OAuth status, get auth URL if needed | _none_ | `{authenticated: bool, auth_url?: str, scopes?: [str]}` |

### Clinical Tools (8)

| Tool | Description | Parameters |
|------|-------------|------------|
| `drchrono_get_patient_summary` | Get patient with demographics, insurance, recent appointments | `patient_id: int` OR `email: str` OR `name: str` |
| `drchrono_search_patients` | Find patients by criteria | `first_name: str?`, `last_name: str?`, `date_of_birth: str?`, `limit: int = 25` |
| `drchrono_create_patient` | Create new patient | `first_name: str`, `last_name: str`, `date_of_birth: str`, `email: str?`, `cell_phone: str?`, `gender: Literal["Male", "Female", "Other", "UNK"]?` |
| `drchrono_update_patient` | Update patient demographics | `patient_id: int`, `email: str?`, `cell_phone: str?`, `address: str?` |
| `drchrono_get_appointments` | List appointments | `date: str`, `patient_id: int?`, `doctor_id: int?`, `status: Literal["", "Confirmed", "Checked In", "In Room", ...]?`, `limit: int = 50` |
| `drchrono_create_appointment` | Schedule appointment | `patient_id: int`, `doctor_id: int`, `scheduled_time: str`, `duration: int = 30`, `office_id: int`, `reason: str?` |
| `drchrono_update_appointment` | Update/cancel appointment | `appointment_id: int`, `status: Literal["Confirmed", "Cancelled", "No Show", "Rescheduled"]?`, `scheduled_time: str?` |
| `drchrono_get_clinical_note` | Get clinical note for appointment | `appointment_id: int`, `format: Literal["raw", "pdf_url"] = "raw"` |
| `drchrono_add_clinical_note` | Add note to appointment | `appointment_id: int`, `chief_complaint: str?`, `notes: str?` |
| `drchrono_get_patient_health_record` | Complete health record (meds, allergies, problems, vaccines) | `patient_id: int` |

### Billing Tools (3)

| Tool | Description | Parameters |
|------|-------------|------------|
| `drchrono_check_eligibility` | Insurance eligibility verification | `patient_id: int`, `insurance_type: Literal["primary", "secondary"] = "primary"` |
| `drchrono_get_billing_summary` | Line items and transactions for patient | `patient_id: int`, `since: str?`, `limit: int = 50` |
| `drchrono_list_transactions` | Payment/adjustment transactions | `since: str`, `patient_id: int?`, `limit: int = 100` |

### Lab & Imaging Tools (3)

| Tool | Description | Parameters |
|------|-------------|------------|
| `drchrono_get_lab_results` | Patient lab results | `patient_id: int`, `since: str?`, `limit: int = 25` |
| `drchrono_list_documents` | Patient uploaded documents | `patient_id: int`, `doc_type: Literal["lab", "imaging", "other"]?`, `limit: int = 25` |
| `drchrono_get_ccda` | Export CCDA XML for patient | `patient_id: int` |

### FHIR Tools (3)

| Tool | Description | Parameters |
|------|-------------|------------|
| `drchrono_fhir_get_patient` | FHIR R4 Patient resource | `patient_id: str` |
| `drchrono_fhir_search` | FHIR bundle search | `resource_type: Literal["Patient", "Observation", "Condition", "MedicationRequest", "AllergyIntolerance", "Immunization", "DiagnosticReport"]`, `params: str` |
| `drchrono_fhir_get_capability_statement` | FHIR server capabilities | _none_ |

## File Structure

```
dr-chrono-mcp/
├── pyproject.toml              # Dependencies, project metadata
├── README.md                   # Setup and usage instructions
├── .env.example                # Template for credentials
├── src/
│   └── drchrono_mcp/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point (FastMCP)
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── oauth.py        # OAuth flow handler
│       │   └── token_store.py  # Secure token persistence
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── rest_client.py  # DrChrono REST API client
│       │   └── fhir_client.py  # FHIR R4 client
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── clinical.py     # Patient, appointment, note tools
│       │   ├── billing.py      # Eligibility, transactions tools
│       │   ├── lab_imaging.py  # Lab results, documents tools
│       │   ├── fhir.py         # FHIR-specific tools
│       │   └── auth_tools.py   # Auth status tool
│       └── models/
│           ├── __init__.py
│           └── types.py        # Pydantic models, Literals
└── docs/                       # Documentation
    └── plans/                  # Design documents
```

## Dependencies

```toml
[project]
dependencies = [
    "mcp>=1.0.0",              # MCP SDK
    "httpx>=0.27.0",           # Async HTTP client
    "pydantic>=2.0",           # Data validation
    "python-dotenv>=1.0.0",    # Environment variables
]
```

## Configuration

Environment variables (`.env`):

```env
# DrChrono OAuth (Required)
DRCHRONO_CLIENT_ID=your_client_id
DRCHRONO_CLIENT_SECRET=your_client_secret
DRCHRONO_REDIRECT_URI=http://localhost:8000/callback

# FHIR/ConnectEHR (Optional)
DRCHRONO_FHIR_BASE_URL=https://your-practice.dynamicfhir.com/fhir/r4
DRCHRONO_FHIR_CLIENT_ID=fhir_client_id
DRCHRONO_FHIR_CLIENT_SECRET=fhir_client_secret

# Token Storage
DRCHRONO_TOKEN_FILE=~/.drchrono/tokens.json
```

## MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "drchrono": {
      "command": "uv",
      "args": ["--directory", "/path/to/dr-chrono-mcp", "run", "drchrono-mcp"],
      "env": {
        "DRCHRONO_CLIENT_ID": "your_client_id",
        "DRCHRONO_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

## Implementation Notes

### Rate Limiting
DrChrono enforces rate limits. The client should:
- Handle 429 responses with exponential backoff
- Use bulk API endpoints where available (page_size up to 1000)
- Cache frequently accessed data (doctors, offices)

### Bulk APIs
For large data retrieval, use async bulk endpoints:
- `POST /api/appointments_list` → `GET /api/appointments_list?uuid=...`
- Supports up to 1000 results per page
- Results cached for 1 hour

### HIPAA Considerations
- Tokens stored with restrictive file permissions (600)
- No PHI logged
- Token refresh happens automatically before expiry

### Health Gorilla Integration
Health Gorilla provides lab ordering through FHIR. When the user's practice has Health Gorilla enabled:
- Lab orders appear in the Health Gorilla tab in patient charts
- Results are returned via FHIR resources
- The MCP server can retrieve these via standard FHIR tools

## Next Steps

1. Initialize Python project with pyproject.toml
2. Implement OAuth flow with token persistence
3. Build REST API client with rate limiting
4. Implement clinical tools
5. Add billing and lab tools
6. Implement FHIR client and tools
7. Write README with setup instructions
8. Test with Claude Desktop
