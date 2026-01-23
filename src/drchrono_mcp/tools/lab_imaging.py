"""Lab and imaging tools: results, documents, CCDA export."""

from typing import Literal

from mcp.server import Server

from drchrono_mcp.clients.rest_client import DrChronoClient


def register_lab_imaging_tools(server: Server, client: DrChronoClient) -> None:
    """Register lab and imaging tools with MCP server.

    Args:
        server: MCP Server instance
        client: DrChrono REST API client
    """

    @server.tool()
    async def drchrono_get_lab_results(
        patient_id: int,
        since: str | None = None,
        limit: int = 25,
    ) -> dict:
        """Get lab results for a patient.

        Returns manual/legacy lab results. For integrated lab results
        (Health Gorilla, Quest, LabCorp), use FHIR tools or check documents.

        Args:
            patient_id: Patient ID (required)
            since: Only results since this date (YYYY-MM-DD)
            limit: Maximum results (default 25)

        Returns:
            List of lab results with values and reference ranges
        """
        results = await client.get_lab_results(patient_id, since=since, limit=limit)

        return {
            "patient_id": patient_id,
            "lab_results": [
                {
                    "id": r["id"],
                    "test_name": r.get("test_name"),
                    "value": r.get("value"),
                    "unit": r.get("unit"),
                    "normal_range": r.get("normal_range"),
                    "abnormal_flag": r.get("abnormal_flag"),
                    "observation_date": r.get("observation_date"),
                    "ordering_doctor": r.get("ordering_doctor"),
                    "lab_name": r.get("lab_name"),
                }
                for r in results.get("results", [])
            ],
            "total_count": results["total_count"],
            "has_more": results["has_more"],
            "note": (
                "For integrated lab results from Health Gorilla, Quest, or LabCorp, "
                "check documents or use FHIR DiagnosticReport search."
            ),
        }

    @server.tool()
    async def drchrono_list_documents(
        patient_id: int,
        doc_type: Literal["lab", "imaging", "consent", "other"] | None = None,
        limit: int = 25,
    ) -> dict:
        """List uploaded documents for a patient.

        Documents include lab reports, imaging results, consent forms,
        and other uploaded files.

        Args:
            patient_id: Patient ID (required)
            doc_type: Filter by type - "lab", "imaging", "consent", or "other"
            limit: Maximum results (default 25)

        Returns:
            List of documents with download URLs (valid for 1 hour)
        """
        results = await client.get_documents(patient_id, limit=limit)

        documents = results.get("results", [])

        # Filter by type if specified
        if doc_type:
            type_map = {
                "lab": ["lab", "laboratory"],
                "imaging": ["imaging", "radiology", "xray", "mri", "ct"],
                "consent": ["consent"],
                "other": [],
            }
            filter_terms = type_map.get(doc_type, [])
            if filter_terms:
                documents = [
                    d for d in documents
                    if any(
                        term.lower() in (d.get("category", "") or "").lower()
                        or term.lower() in (d.get("description", "") or "").lower()
                        for term in filter_terms
                    )
                ]

        return {
            "patient_id": patient_id,
            "documents": [
                {
                    "id": d["id"],
                    "description": d.get("description"),
                    "category": d.get("category"),
                    "date": d.get("date"),
                    "document_url": d.get("document"),  # URL with token (1 hour validity)
                    "metatags": d.get("metatags"),
                }
                for d in documents[:limit]
            ],
            "total_count": len(documents),
            "note": "Document URLs contain a token valid for 1 hour. Download before expiry.",
        }

    @server.tool()
    async def drchrono_get_ccda(patient_id: int) -> dict:
        """Export CCDA (Consolidated Clinical Document Architecture) for a patient.

        CCDA is a standardized XML format containing:
        - Patient demographics
        - Medications
        - Allergies
        - Problems/conditions
        - Procedures
        - Immunizations
        - Lab results
        - Vital signs

        Useful for data portability and interoperability.

        Args:
            patient_id: Patient ID (required)

        Returns:
            CCDA XML content or download URL
        """
        result = await client.get_ccda(patient_id)

        # CCDA endpoint returns XML or URL depending on configuration
        if isinstance(result, str):
            # Direct XML content
            return {
                "patient_id": patient_id,
                "format": "xml",
                "content": result,
                "content_type": "application/xml",
            }
        elif isinstance(result, dict):
            # URL to download
            return {
                "patient_id": patient_id,
                "format": "url",
                "download_url": result.get("url") or result.get("ccda"),
                "note": "URL is temporary. Download within 1 hour.",
            }
        else:
            return {
                "patient_id": patient_id,
                "error": "Unexpected CCDA response format",
                "raw_result": str(result)[:500],
            }
