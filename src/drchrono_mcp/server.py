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

# Create FastMCP server
mcp = FastMCP("drchrono-mcp")

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
    """Start DrChrono OAuth flow - opens browser for authorization."""
    oauth = get_oauth()
    if oauth.is_authenticated:
        return {"message": "Already authenticated", "authenticated": True}

    auth_url = oauth.get_authorization_url()
    import webbrowser

    webbrowser.open(auth_url)
    return {
        "message": "Browser opened for authorization. Complete the flow.",
        "auth_url": auth_url,
    }


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


def main():
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="DrChrono MCP Server")
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run as HTTP server with SSE transport (for remote clients)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)",
    )
    args = parser.parse_args()

    if args.sse:
        import uvicorn

        print(f"Starting DrChrono MCP server on http://{args.host}:{args.port}")
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
