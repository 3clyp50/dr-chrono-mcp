# DrChrono MCP Server

A Model Context Protocol (MCP) server for the [DrChrono](https://www.drchrono.com/) healthcare API, providing tools for patient management, appointments, clinical notes, billing, and FHIR R4 interoperability.

## Features

- **OAuth 2.0 Authentication** - Secure authorization flow with automatic token refresh
- **Patient Management** - Search, create, and update patient records
- **Appointments** - Schedule, update, and query appointments
- **Clinical Notes** - Read and update clinical documentation
- **Health Records** - Access medications, allergies, problems, and immunizations
- **Billing** - Check eligibility, view charges and transactions
- **Lab & Imaging** - Retrieve lab results and uploaded documents
- **FHIR R4** - Standardized healthcare data access via ConnectEHR

## Prerequisites

1. **DrChrono Account** with API access
2. **Python 3.11+**
3. **uv** (recommended) or pip

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dr-chrono-mcp.git
cd dr-chrono-mcp

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Configuration

### 1. Create DrChrono API Application

1. Log in to DrChrono
2. Go to **Account** > **API**
3. Click **New Application**
4. Set:
   - **Name**: Your app name
   - **Redirect URI**: `http://localhost:8765/callback`
5. Save and copy your **Client ID** and **Client Secret**

### 2. Set Environment Variables

Copy the example file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DRCHRONO_CLIENT_ID=your_client_id
DRCHRONO_CLIENT_SECRET=your_client_secret
DRCHRONO_REDIRECT_URI=http://localhost:8765/callback
```

### 3. (Optional) Configure FHIR Access

For FHIR R4 tools, set up ConnectEHR:

1. Go to **Account** > **API** > **ConnectEHR Setup for FHIR**
2. Complete the setup form
3. Add to `.env`:

```env
DRCHRONO_FHIR_BASE_URL=https://your-practice.dynamicfhir.com/fhir/r4
DRCHRONO_FHIR_CLIENT_ID=fhir_client_id
DRCHRONO_FHIR_CLIENT_SECRET=fhir_client_secret
```

## Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

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

### With Other MCP Clients

```bash
# Run the server directly
uv run drchrono-mcp

# Or with environment variables
DRCHRONO_CLIENT_ID=xxx DRCHRONO_CLIENT_SECRET=yyy uv run drchrono-mcp
```

## Authentication Flow

1. Use the `drchrono_auth_status` tool to check authentication
2. If not authenticated, visit the provided `auth_url` in a browser
3. Log in to DrChrono and authorize the application
4. Tokens are automatically saved and refreshed

## Available Tools

### Authentication
| Tool | Description |
|------|-------------|
| `drchrono_auth_status` | Check OAuth status, get auth URL |
| `drchrono_start_auth` | Start browser-based authorization |
| `drchrono_logout` | Clear stored credentials |

### Clinical
| Tool | Description |
|------|-------------|
| `drchrono_get_patient_summary` | Get patient with demographics, insurance, appointments |
| `drchrono_search_patients` | Search by name, DOB, email |
| `drchrono_create_patient` | Create new patient |
| `drchrono_update_patient` | Update demographics |
| `drchrono_get_appointments` | List appointments with filters |
| `drchrono_create_appointment` | Schedule appointment |
| `drchrono_update_appointment` | Update/cancel appointment |
| `drchrono_get_clinical_note` | Get note for appointment |
| `drchrono_add_clinical_note` | Update clinical note |
| `drchrono_get_patient_health_record` | Get meds, allergies, problems, vaccines |

### Billing
| Tool | Description |
|------|-------------|
| `drchrono_check_eligibility` | Verify insurance coverage |
| `drchrono_get_billing_summary` | Charges, payments, balance |
| `drchrono_list_transactions` | Payment transactions |

### Lab & Imaging
| Tool | Description |
|------|-------------|
| `drchrono_get_lab_results` | Patient lab results |
| `drchrono_list_documents` | Uploaded documents |
| `drchrono_get_ccda` | Export CCDA XML |

### FHIR R4
| Tool | Description |
|------|-------------|
| `drchrono_fhir_get_patient` | FHIR Patient resource |
| `drchrono_fhir_search` | Search any FHIR resource |
| `drchrono_fhir_get_capability_statement` | Server capabilities |
| `drchrono_fhir_patient_everything` | All patient data |

## Example Workflows

### Get Today's Appointments
```
Use drchrono_get_appointments with date="2024-01-15"
```

### Find and Update a Patient
```
1. drchrono_search_patients with last_name="Smith"
2. drchrono_update_patient with patient_id and new email
```

### Check Patient Eligibility
```
1. drchrono_search_patients to find patient
2. drchrono_check_eligibility with patient_id
```

### Export Patient Data (FHIR)
```
drchrono_fhir_patient_everything with patient_id
```

## Security Notes

- Tokens are stored in `~/.drchrono/tokens.json` with restricted permissions (600)
- Never commit `.env` or token files to version control
- HIPAA: Access only data you're authorized to view
- Token refresh happens automatically before expiry

## Troubleshooting

### "Not authenticated" error
Run `drchrono_auth_status` and follow the authorization flow.

### "Rate limited" errors
The server handles 429 responses automatically with backoff. For bulk operations, use appropriate date ranges.

### FHIR tools show "not configured"
FHIR requires separate ConnectEHR setup. See Configuration section.

### Token refresh fails
Delete `~/.drchrono/tokens.json` and re-authenticate.

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run linting
uv run ruff check src/

# Format code
uv run ruff format src/
```

## License

MIT

## Resources

- [DrChrono API Documentation](https://app.drchrono.com/api-docs/)
- [DrChrono FHIR Setup](https://support.drchrono.com/home/set-up-connectehr-for-fhir)
- [Model Context Protocol](https://modelcontextprotocol.io/)