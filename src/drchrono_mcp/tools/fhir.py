"""FHIR R4 tools for interoperability and standardized data access."""

from mcp.server import Server

from drchrono_mcp.clients.fhir_client import FHIRClient
from drchrono_mcp.models.types import FHIRResourceType


def register_fhir_tools(server: Server, fhir_client: FHIRClient | None) -> None:
    """Register FHIR tools with MCP server.

    Args:
        server: MCP Server instance
        fhir_client: FHIR client (may be None if not configured)
    """

    def _check_configured():
        """Check if FHIR is configured."""
        if not fhir_client or not fhir_client.is_configured:
            return {
                "error": "FHIR not configured",
                "message": (
                    "FHIR access requires ConnectEHR credentials. "
                    "Set DRCHRONO_FHIR_BASE_URL, DRCHRONO_FHIR_CLIENT_ID, "
                    "and DRCHRONO_FHIR_CLIENT_SECRET environment variables."
                ),
                "setup_instructions": [
                    "1. Go to DrChrono Account > API > ConnectEHR Setup for FHIR",
                    "2. Complete the FHIR setup form",
                    "3. Copy your FHIR base URL and credentials",
                    "4. Set the environment variables and restart the MCP server",
                ],
            }
        return None

    @server.tool()
    async def drchrono_fhir_get_patient(patient_id: str) -> dict:
        """Get FHIR R4 Patient resource.

        Returns patient data in standardized FHIR format.
        Useful for interoperability with other healthcare systems.

        Args:
            patient_id: FHIR Patient resource ID (required)

        Returns:
            FHIR Patient resource
        """
        error = _check_configured()
        if error:
            return error

        try:
            patient = await fhir_client.get_patient(patient_id)
            return {
                "resourceType": "Patient",
                "id": patient.get("id"),
                "identifier": patient.get("identifier", []),
                "name": patient.get("name", []),
                "birthDate": patient.get("birthDate"),
                "gender": patient.get("gender"),
                "address": patient.get("address", []),
                "telecom": patient.get("telecom", []),
                "communication": patient.get("communication", []),
                "_raw": patient,  # Full FHIR resource
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to fetch FHIR Patient resource",
            }

    @server.tool()
    async def drchrono_fhir_search(
        resource_type: FHIRResourceType,
        patient_id: str | None = None,
        params: str | None = None,
    ) -> dict:
        """Search for FHIR resources.

        Search any FHIR R4 resource type with optional parameters.

        Args:
            resource_type: FHIR resource type - Patient, Observation, Condition,
                MedicationRequest, AllergyIntolerance, Immunization, DiagnosticReport,
                Procedure, Encounter, or DocumentReference
            patient_id: Filter by patient (optional for most searches)
            params: Additional FHIR search params (e.g., "category=vital-signs")

        Returns:
            FHIR Bundle with search results
        """
        error = _check_configured()
        if error:
            return error

        try:
            # Build search params
            search_params = {}
            if patient_id:
                search_params["patient"] = patient_id
            if params:
                # Parse query string params
                for pair in params.split("&"):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        search_params[key] = value

            bundle = await fhir_client.search(resource_type, search_params)

            # Extract entries
            entries = bundle.get("entry", [])

            return {
                "resourceType": "Bundle",
                "type": bundle.get("type", "searchset"),
                "total": bundle.get("total", len(entries)),
                "entries": [
                    {
                        "resourceType": e.get("resource", {}).get("resourceType"),
                        "id": e.get("resource", {}).get("id"),
                        "resource": e.get("resource"),
                    }
                    for e in entries[:50]  # Limit entries in response
                ],
                "has_more": len(entries) > 50,
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to search {resource_type} resources",
            }

    @server.tool()
    async def drchrono_fhir_get_capability_statement() -> dict:
        """Get FHIR server capability statement.

        Returns metadata about the FHIR server including:
        - Supported resource types
        - Available search parameters
        - Supported operations
        - Security requirements

        Useful for understanding what FHIR operations are available.

        Returns:
            FHIR CapabilityStatement resource
        """
        error = _check_configured()
        if error:
            return error

        try:
            capability = await fhir_client.get_capability_statement()

            # Extract key information
            rest = capability.get("rest", [{}])[0]
            resources = rest.get("resource", [])

            return {
                "fhirVersion": capability.get("fhirVersion"),
                "status": capability.get("status"),
                "publisher": capability.get("publisher"),
                "supported_resources": [
                    {
                        "type": r.get("type"),
                        "interactions": [i.get("code") for i in r.get("interaction", [])],
                        "searchParams": [p.get("name") for p in r.get("searchParam", [])],
                    }
                    for r in resources[:20]  # Limit to first 20
                ],
                "security": rest.get("security", {}),
                "total_resources": len(resources),
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to fetch FHIR capability statement",
            }

    @server.tool()
    async def drchrono_fhir_patient_everything(patient_id: str) -> dict:
        """Get all FHIR data for a patient using $everything operation.

        Returns a comprehensive Bundle containing all resources
        associated with a patient: conditions, medications, observations,
        allergies, immunizations, procedures, encounters, etc.

        This is a convenient way to get a complete patient record in
        FHIR format for data portability or analysis.

        Note: Not all FHIR servers support this operation.

        Args:
            patient_id: FHIR Patient resource ID (required)

        Returns:
            FHIR Bundle with all patient resources
        """
        error = _check_configured()
        if error:
            return error

        try:
            bundle = await fhir_client.get_patient_everything(patient_id)

            # Summarize the bundle
            entries = bundle.get("entry", [])
            resource_counts = {}
            for entry in entries:
                resource_type = entry.get("resource", {}).get("resourceType", "Unknown")
                resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1

            return {
                "patient_id": patient_id,
                "total_resources": len(entries),
                "resource_summary": resource_counts,
                "entries": [
                    {
                        "resourceType": e.get("resource", {}).get("resourceType"),
                        "id": e.get("resource", {}).get("id"),
                    }
                    for e in entries[:100]  # Summary only
                ],
                "full_bundle_available": True,
                "note": "Use drchrono_fhir_search for specific resource types if needed.",
            }
        except Exception as e:
            if "not supported" in str(e).lower() or "not implemented" in str(e).lower():
                return {
                    "error": "Operation not supported",
                    "message": (
                        "The $everything operation is not supported by this FHIR server. "
                        "Use drchrono_fhir_search to query specific resource types instead."
                    ),
                    "alternative": "drchrono_fhir_search",
                }
            return {
                "error": str(e),
                "message": "Failed to execute $everything operation",
            }
