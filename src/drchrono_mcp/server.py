"""DrChrono MCP Server - Main entry point.

This MCP server provides tools for interacting with the DrChrono healthcare API,
including patient management, appointments, clinical notes, billing, FHIR access,
and persistent clinical memory via SimpleMem.

Supports two transport modes:
- stdio (default): For local MCP clients that spawn the server
- sse: HTTP server for remote clients (e.g., Docker containers)

Run with SSE: drchrono-mcp --sse --port 8080
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

# Load environment variables
load_dotenv()


def get_env_or_error(name: str) -> str:
    """Get required environment variable or exit with helpful error."""
    value = os.getenv(name)
    if not value:
        print(f"Error: Required environment variable {name} is not set.", file=sys.stderr)
        print(f"Please set {name} in your environment or .env file.", file=sys.stderr)
        sys.exit(1)
    return value


# Get OAuth credentials
client_id = get_env_or_error("DRCHRONO_CLIENT_ID")
client_secret = get_env_or_error("DRCHRONO_CLIENT_SECRET")
redirect_uri = os.getenv("DRCHRONO_REDIRECT_URI", "http://localhost:8765/callback")

# Create FastMCP server with DNS rebinding protection disabled for local SSE access.
# This is safe for a localhost development tool - the protection is mainly needed
# for servers exposed to the internet.
mcp = FastMCP(
    "drchrono-mcp",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

# Lazy-initialized clients (initialized on first use)
_oauth = None
_rest_client = None
_fhir_client = None
_memory_client = None


def get_oauth():
    """Get or create OAuth manager."""
    global _oauth
    if _oauth is None:
        from drchrono_mcp.auth.oauth import OAuthManager
        from drchrono_mcp.auth.token_store import TokenStore

        token_file = os.getenv("DRCHRONO_TOKEN_FILE")
        token_store = TokenStore(token_file) if token_file else TokenStore()
        _oauth = OAuthManager(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_store=token_store,
        )
    return _oauth


def get_rest_client():
    """Get or create REST client."""
    global _rest_client
    if _rest_client is None:
        from drchrono_mcp.clients.rest_client import DrChronoClient

        _rest_client = DrChronoClient(get_oauth())
    return _rest_client


def get_fhir_client():
    """Get or create FHIR client (optional)."""
    global _fhir_client
    if _fhir_client is None:
        fhir_base_url = os.getenv("DRCHRONO_FHIR_BASE_URL")
        if fhir_base_url:
            from drchrono_mcp.clients.fhir_client import FHIRClient

            _fhir_client = FHIRClient(
                base_url=fhir_base_url,
                client_id=os.getenv("DRCHRONO_FHIR_CLIENT_ID"),
                client_secret=os.getenv("DRCHRONO_FHIR_CLIENT_SECRET"),
            )
    return _fhir_client


def get_memory_client():
    """Get or create SimpleMem client (optional)."""
    global _memory_client
    if _memory_client is None:
        simplemem_url = os.getenv("SIMPLEMEM_API_URL")
        simplemem_token = os.getenv("SIMPLEMEM_ACCESS_TOKEN")
        if simplemem_url and simplemem_token:
            from drchrono_mcp.clients.simplemem_client import SimpleMemClient

            _memory_client = SimpleMemClient(
                api_url=simplemem_url,
                access_token=simplemem_token,
            )
    return _memory_client


# ============================================
# AUTH TOOLS
# ============================================


@mcp.tool()
async def drchrono_auth_status() -> dict:
    """Check DrChrono OAuth authentication status.

    Use this tool to:
    - Check if you're authenticated with DrChrono
    - Get the authorization URL if authentication is needed
    """
    oauth = get_oauth()
    if oauth.is_authenticated:
        return {
            "authenticated": True,
            "message": "Authenticated with DrChrono API. Ready to make requests.",
        }
    else:
        auth_url = oauth.get_authorization_url()
        return {
            "authenticated": False,
            "auth_url": auth_url,
            "message": "Not authenticated. Visit the auth_url to authorize.",
        }


@mcp.tool()
async def drchrono_start_auth() -> dict:
    """Start DrChrono OAuth flow - opens browser for authorization.

    After authorizing in browser, you'll be redirected to a URL like:
    http://localhost:8765/callback?code=XXXXX

    Copy the 'code' value and use drchrono_exchange_code to complete auth.
    """
    oauth = get_oauth()
    if oauth.is_authenticated:
        return {"message": "Already authenticated", "authenticated": True}

    auth_url = oauth.get_authorization_url()
    import webbrowser

    webbrowser.open(auth_url)
    return {
        "message": (
            "Browser opened for authorization. After authorizing, "
            "copy the 'code' parameter from the redirect URL and use "
            "drchrono_exchange_code to complete authentication."
        ),
        "auth_url": auth_url,
    }


@mcp.tool()
async def drchrono_exchange_code(code: str) -> dict:
    """Exchange authorization code for access tokens.

    Use this after drchrono_start_auth. When the browser redirects to
    localhost:8765/callback?code=XXXXX, copy the code value and pass it here.

    Args:
        code: The authorization code from the callback URL
    """
    oauth = get_oauth()
    if oauth.is_authenticated:
        return {"message": "Already authenticated", "authenticated": True}

    try:
        tokens = await oauth.exchange_code(code)
        return {
            "authenticated": True,
            "message": "Successfully authenticated with DrChrono API.",
            "expires_at": tokens.expires_at.isoformat(),
            "scopes": tokens.scope.split() if tokens.scope else [],
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "message": (
                "Failed to exchange code. The code may have expired "
                "(they're only valid for a few minutes). Try drchrono_start_auth again."
            ),
        }


@mcp.tool()
async def drchrono_logout() -> dict:
    """Clear stored DrChrono credentials and log out."""
    oauth = get_oauth()
    oauth.logout()
    return {"message": "Logged out. Stored tokens have been deleted."}


# ============================================
# CLINICAL TOOLS
# ============================================


@mcp.tool()
async def drchrono_search_patients(
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: str | None = None,
    email: str | None = None,
) -> dict:
    """Search for patients by name, DOB, or email.

    Args:
        first_name: Patient first name
        last_name: Patient last name
        date_of_birth: Date of birth (YYYY-MM-DD)
        email: Patient email
    """
    client = get_rest_client()
    return await client.search_patients(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        email=email,
    )


@mcp.tool()
async def drchrono_get_patient(patient_id: int) -> dict:
    """Get patient details by ID.

    Args:
        patient_id: The patient's ID
    """
    client = get_rest_client()
    return await client.get_patient(patient_id, verbose=True)


@mcp.tool()
async def drchrono_get_appointments(
    patient_id: int | None = None,
    since: str | None = None,
    date: str | None = None,
) -> dict:
    """List appointments with optional filters.

    Args:
        patient_id: Filter by patient ID
        since: Show appointments since this date (YYYY-MM-DD)
        date: Show appointments on this specific date (YYYY-MM-DD)
    """
    client = get_rest_client()
    return await client.get_appointments(patient_id=patient_id, since=since, date=date)


@mcp.tool()
async def drchrono_get_medications(patient_id: int) -> dict:
    """Get patient's medications.

    Args:
        patient_id: The patient's ID
    """
    client = get_rest_client()
    return await client.get_medications(patient_id)


@mcp.tool()
async def drchrono_get_allergies(patient_id: int) -> dict:
    """Get patient's allergies - CRITICAL for prescribing.

    Args:
        patient_id: The patient's ID
    """
    client = get_rest_client()
    return await client.get_allergies(patient_id)


@mcp.tool()
async def drchrono_get_problems(patient_id: int) -> dict:
    """Get patient's active problems/conditions.

    Args:
        patient_id: The patient's ID
    """
    client = get_rest_client()
    return await client.get_problems(patient_id)


@mcp.tool()
async def drchrono_get_lab_results(
    patient_id: int,
    since: str | None = None,
) -> dict:
    """Get patient's lab results.

    Args:
        patient_id: The patient's ID
        since: Show results since this date (YYYY-MM-DD)
    """
    client = get_rest_client()
    return await client.get_lab_results(patient_id, since=since)


@mcp.tool()
async def drchrono_get_clinical_note(appointment_id: int) -> dict:
    """Get clinical note for an appointment.

    Args:
        appointment_id: The appointment ID
    """
    client = get_rest_client()
    return await client.get_clinical_note(appointment_id)


# ============================================
# CLINICAL CONTEXT (PRIMARY TOOL)
# ============================================


@mcp.tool()
async def drchrono_get_clinical_context(
    patient_id: int | None = None,
    appointment_id: int | None = None,
) -> dict:
    """Get COMPLETE clinical context for a patient visit.

    This is the PRIMARY tool for doctors. Returns ALL clinically relevant
    information: demographics, medications, allergies, problems, labs, notes.

    Args:
        patient_id: Patient ID (provide this OR appointment_id)
        appointment_id: Current appointment ID (will auto-fetch patient)
    """
    import asyncio
    from datetime import datetime, timedelta

    client = get_rest_client()

    # Resolve patient from appointment if needed
    if appointment_id and not patient_id:
        apt = await client.get_appointment(appointment_id)
        patient_id = apt.get("patient")
        if not patient_id:
            return {"error": f"No patient found for appointment {appointment_id}"}

    if not patient_id:
        return {"error": "Provide patient_id or appointment_id"}

    # Fetch all data in parallel
    since_90_days = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    patient, meds, allergies, problems, labs = await asyncio.gather(
        client.get_patient(patient_id, verbose=True),
        client.get_medications(patient_id),
        client.get_allergies(patient_id),
        client.get_problems(patient_id),
        client.get_lab_results(patient_id, since=since_90_days),
        return_exceptions=True,
    )

    def safe_get(result, key="results"):
        if isinstance(result, Exception):
            return {"error": str(result)}
        return result.get(key, []) if isinstance(result, dict) else result

    context = {
        "patient_id": patient_id,
        "retrieved_at": datetime.now().isoformat(),
        "demographics": {
            "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
            "date_of_birth": patient.get("date_of_birth"),
            "gender": patient.get("gender"),
        }
        if isinstance(patient, dict)
        else {"error": str(patient)},
        "allergies": safe_get(allergies),
        "medications": safe_get(meds),
        "problems": safe_get(problems),
        "recent_labs": safe_get(labs),
    }

    # Add memories if configured
    memory = get_memory_client()
    if memory and memory.is_configured:
        try:
            patient_name = context["demographics"].get("name", "")
            memories = await memory.get_patient_memories(patient_id, patient_name)
            context["past_encounters"] = memories.get("content", [])
        except Exception as e:
            context["past_encounters"] = {"error": str(e)}

    return context


# ============================================
# MEMORY TOOLS
# ============================================


@mcp.tool()
async def drchrono_store_encounter_memory(
    patient_id: int,
    encounter_summary: str,
    chief_complaint: str | None = None,
    diagnosis: str | None = None,
    plan: str | None = None,
) -> dict:
    """Store encounter summary in persistent memory for future visits.

    Args:
        patient_id: Patient ID
        encounter_summary: Brief summary of the encounter
        chief_complaint: Chief complaint for this visit
        diagnosis: Diagnosis (comma-separated if multiple)
        plan: Treatment plan
    """
    memory = get_memory_client()
    if not memory or not memory.is_configured:
        return {"error": "SimpleMem not configured"}

    client = get_rest_client()
    patient = await client.get_patient(patient_id)
    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"

    from datetime import datetime

    diagnosis_list = [d.strip() for d in diagnosis.split(",")] if diagnosis else None

    result = await memory.store_patient_encounter(
        patient_id=patient_id,
        patient_name=patient_name,
        encounter_summary=encounter_summary,
        visit_date=datetime.now().strftime("%Y-%m-%d"),
        chief_complaint=chief_complaint,
        diagnosis=diagnosis_list,
        plan=plan,
    )
    return {"success": True, "result": result}


@mcp.tool()
async def drchrono_search_patient_history(
    patient_id: int,
    query: str,
) -> dict:
    """Search patient's clinical history in memory system.

    Args:
        patient_id: Patient ID
        query: Search query (e.g., "diabetes management", "cardiac workup")
    """
    memory = get_memory_client()
    if not memory or not memory.is_configured:
        return {"error": "SimpleMem not configured"}

    client = get_rest_client()
    patient = await client.get_patient(patient_id)
    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"

    full_query = f"patient_id:{patient_id} {patient_name} {query}"
    results = await memory.search_memories(full_query, limit=10)
    return {"patient_id": patient_id, "query": query, "results": results.get("content", [])}


# ============================================
# BILLING & ELIGIBILITY TOOLS
# ============================================


@mcp.tool()
async def drchrono_check_eligibility(
    patient_id: int,
    insurance_type: str = "primary",
) -> dict:
    """Check insurance eligibility for a patient.

    Verifies patient's insurance coverage status with the payer.
    Returns the most recent eligibility check result.

    Args:
        patient_id: Patient ID (required)
        insurance_type: Which insurance to check - "primary", "secondary", or "tertiary"

    Returns:
        Eligibility status and coverage details
    """
    client = get_rest_client()
    results = await client.check_eligibility(patient_id, insurance_type)

    if not results.get("results"):
        return {
            "patient_id": patient_id,
            "insurance_type": insurance_type,
            "has_eligibility": False,
            "message": f"No eligibility check found for {insurance_type} insurance",
        }

    # Get most recent eligibility check
    latest = results["results"][0]

    return {
        "patient_id": patient_id,
        "insurance_type": insurance_type,
        "has_eligibility": True,
        "eligibility_id": latest.get("id"),
        "status": latest.get("status"),
        "payer_name": latest.get("payer_name"),
        "subscriber_id": latest.get("subscriber_id"),
        "group_number": latest.get("group_number"),
        "coverage_active": latest.get("coverage_active"),
        "copay": latest.get("copay"),
        "deductible": latest.get("deductible"),
        "deductible_remaining": latest.get("deductible_remaining"),
        "check_date": latest.get("check_date"),
    }


@mcp.tool()
async def drchrono_get_billing_summary(
    patient_id: int,
    since: str | None = None,
    limit: int = 50,
) -> dict:
    """Get billing summary for a patient.

    Includes line items (charges) and recent transactions (payments).
    Calculates outstanding balance.

    Args:
        patient_id: Patient ID (required)
        since: Only include items since this date (YYYY-MM-DD)
        limit: Maximum items per category (default 50)

    Returns:
        Billing summary with charges, payments, and balance
    """
    import asyncio

    client = get_rest_client()
    line_items, transactions = await asyncio.gather(
        client.get_line_items(patient_id=patient_id, since=since, limit=limit),
        client.get_transactions(
            since=since or "2020-01-01", patient_id=patient_id, limit=limit
        ),
    )

    total_charges = sum(
        float(item.get("price", 0) or 0) * int(item.get("units", 1) or 1)
        for item in line_items.get("results", [])
    )
    total_payments = sum(
        float(t.get("amount", 0) or 0)
        for t in transactions.get("results", [])
        if t.get("type") == "payment"
    )
    total_adjustments = sum(
        float(t.get("amount", 0) or 0)
        for t in transactions.get("results", [])
        if t.get("type") == "adjustment"
    )

    balance = total_charges - total_payments - abs(total_adjustments)

    return {
        "patient_id": patient_id,
        "total_charges": round(total_charges, 2),
        "total_payments": round(total_payments, 2),
        "total_adjustments": round(total_adjustments, 2),
        "balance": round(balance, 2),
        "line_items_count": len(line_items.get("results", [])),
        "transactions_count": len(transactions.get("results", [])),
    }


# ============================================
# VISUALIZATION TOOLS (MCP-UI)
# ============================================


def _generate_lab_chart_html(labs: list, patient_name: str, patient_data: dict) -> str:
    """Generate HTML with Chart.js for lab results visualization.

    Uses the new themed UI component library for consistent styling.
    """
    from drchrono_mcp.ui.components import LabPanel, PatientHeader
    from drchrono_mcp.ui.theme import generate_full_stylesheet

    # Build patient header
    header = PatientHeader(
        first_name=patient_data.get("first_name", ""),
        last_name=patient_data.get("last_name", ""),
        date_of_birth=patient_data.get("date_of_birth"),
        gender=patient_data.get("gender"),
        patient_id=patient_data.get("id"),
    )

    # Build lab panel with chart
    lab_panel = LabPanel(
        lab_results=labs,
        show_chart=True,
        title="Lab Results",
    )

    stylesheet = generate_full_stylesheet()

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab Results: {patient_name}</title>
    <style>{stylesheet}</style>
</head>
<body>
    <div style="max-width: 900px; margin: 0 auto; padding: var(--space-6);">
        {header.build()}
        <div style="margin-top: var(--space-6);">
            {lab_panel.build()}
        </div>
    </div>
</body>
</html>'''


def _generate_patient_dashboard_html(context: dict, patient_data: dict) -> str:
    """Generate HTML dashboard for patient clinical context.

    Uses the new themed UI component library for consistent styling.
    """
    from drchrono_mcp.ui.components import (
        AllergyList,
        ClinicalCard,
        LabPanel,
        MedicationList,
        PatientHeader,
    )
    from drchrono_mcp.ui.theme import generate_full_stylesheet

    # Build patient header
    demo = context.get("demographics", {})
    demo_name = demo.get("name", "")
    demo_parts = demo_name.split() if demo_name else []
    first = patient_data.get("first_name", demo_parts[0] if demo_parts else "")
    last = patient_data.get("last_name", demo_parts[-1] if demo_parts else "")
    header = PatientHeader(
        first_name=first,
        last_name=last,
        date_of_birth=patient_data.get("date_of_birth", demo.get("date_of_birth")),
        gender=patient_data.get("gender", demo.get("gender")),
        patient_id=context.get("patient_id"),
    )

    # Build clinical sections
    allergies = context.get("allergies", [])
    allergy_data = allergies if isinstance(allergies, list) else []
    allergy_list = AllergyList(allergies=allergy_data)

    medications = context.get("medications", [])
    med_data = medications if isinstance(medications, list) else []
    medication_list = MedicationList(medications=med_data)

    labs = context.get("recent_labs", [])
    lab_panel = LabPanel(
        lab_results=labs if isinstance(labs, list) else [],
        show_chart=False,
        title="Recent Labs",
    )

    # Build problems section
    problems = context.get("problems", [])
    problems_content = ""
    if isinstance(problems, list) and problems:
        problem_items = "".join(
            f'<div class="problem-item">{p.get("name", p.get("description", "Unknown"))}</div>'
            for p in problems
        )
        problems_card = ClinicalCard(
            title="Active Problems",
            icon="clipboard",
            severity="warning",
            badge_text=f"{len(problems)} active",
        )
        problems_card.add_child(f'<div class="problems-list">{problem_items}</div>')
        problems_content = problems_card.build()

    stylesheet = generate_full_stylesheet()

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Dashboard</title>
    <style>
        {stylesheet}
        .dashboard {{ max-width: 960px; margin: 0 auto; padding: var(--space-6); }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--space-4);
            margin-top: var(--space-4);
        }}
        .problem-item {{
            padding: var(--space-2) var(--space-3);
            border-bottom: 1px solid var(--border-secondary);
            font-size: 0.8125rem;
        }}
        .problem-item:last-child {{ border-bottom: none; }}
    </style>
</head>
<body>
    <div class="dashboard">
        {header.build()}
        <div class="dashboard-grid">
            <div>{allergy_list.build()}</div>
            <div>{medication_list.build()}</div>
        </div>
        <div class="dashboard-grid">
            <div>{lab_panel.build()}</div>
            <div>{problems_content}</div>
        </div>
    </div>
</body>
</html>'''


@mcp.tool()
async def drchrono_visualize_labs(
    patient_id: int,
    since: str | None = None,
) -> dict:
    """Generate an interactive lab results chart for a patient.

    Returns an MCP-UI resource with a Chart.js visualization of lab values over time.
    Use this when the doctor wants to SEE lab trends visually.

    The response contains a 'content' array with an MCP-UI resource that clients
    supporting MCP-UI (like Agent Zero with MCP-UI) will render as an interactive chart.

    Args:
        patient_id: The patient's ID
        since: Show results since this date (YYYY-MM-DD)
    """
    from mcp_ui import CreateUIResourceOptions, RawHtmlContent, create_ui_resource

    client = get_rest_client()

    # Fetch patient and labs in parallel
    import asyncio

    patient, labs = await asyncio.gather(
        client.get_patient(patient_id),
        client.get_lab_results(patient_id, since=since),
    )

    patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"
    lab_results = labs.get("results", [])

    if not lab_results:
        return {"message": f"No lab results found for patient {patient_id}"}

    html = _generate_lab_chart_html(lab_results, patient_name, patient)

    resource = create_ui_resource(CreateUIResourceOptions(
        uri=f"ui://drchrono/labs/{patient_id}",
        content=RawHtmlContent(type="rawHtml", htmlString=html),
        encoding="text",
    ))

    return {
        "content": [resource],
        "metadata": {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "lab_count": len(lab_results),
        },
    }


@mcp.tool()
async def drchrono_visualize_patient_dashboard(
    patient_id: int,
) -> dict:
    """Generate a visual patient dashboard with allergies, medications, and problems.

    Returns an MCP-UI resource with a clinical summary card.
    Use this when the doctor wants a quick VISUAL overview of the patient.

    The response contains a 'content' array with an MCP-UI resource that clients
    supporting MCP-UI will render as an interactive dashboard.

    Args:
        patient_id: The patient's ID
    """
    from mcp_ui import CreateUIResourceOptions, RawHtmlContent, create_ui_resource

    client = get_rest_client()

    # Fetch patient data and clinical context in parallel
    import asyncio

    patient, context = await asyncio.gather(
        client.get_patient(patient_id),
        drchrono_get_clinical_context(patient_id=patient_id),
    )

    if "error" in context:
        return context

    html = _generate_patient_dashboard_html(context, patient)

    resource = create_ui_resource(CreateUIResourceOptions(
        uri=f"ui://drchrono/dashboard/{patient_id}",
        content=RawHtmlContent(type="rawHtml", htmlString=html),
        encoding="text",
    ))

    return {
        "content": [resource],
        "metadata": {
            "patient_id": patient_id,
            "patient_name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
        },
    }


def main():
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="DrChrono MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run as HTTP server with Streamable HTTP transport",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run as HTTP server with SSE transport (deprecated, use --http)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)",
    )
    args = parser.parse_args()

    if args.http:
        import uvicorn

        print("Starting DrChrono MCP server (Streamable HTTP)")
        print(f"MCP Endpoint: http://{args.host}:{args.port}/mcp")
        uvicorn.run(
            mcp.streamable_http_app(),
            host=args.host,
            port=args.port,
            log_level="info",
        )
    elif args.sse:
        import uvicorn

        print("WARNING: SSE transport is deprecated. Use --http instead.")
        print(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        uvicorn.run(
            mcp.sse_app(),
            host=args.host,
            port=args.port,
            log_level="info",
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
