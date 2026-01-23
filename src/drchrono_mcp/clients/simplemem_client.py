"""SimpleMem MCP client for persistent clinical memory across sessions."""

from datetime import datetime
from typing import Any

import httpx


class SimpleMemClient:
    """Client for SimpleMem cloud memory service.

    SimpleMem provides persistent memory storage with:
    - Semantic search (vector embeddings)
    - Lexical search (BM25 keywords)
    - Symbolic search (timestamps, entities, metadata)

    Used to maintain clinical context across patient visits and sessions.
    """

    def __init__(self, api_url: str, access_token: str):
        """Initialize SimpleMem client.

        Args:
            api_url: SimpleMem API endpoint (e.g., https://mcp.simplemem.cloud/mcp)
            access_token: Bearer token for authentication
        """
        self.api_url = api_url.rstrip("/")
        self.access_token = access_token
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if SimpleMem is properly configured."""
        return bool(self.api_url and self.access_token)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a SimpleMem MCP tool via JSON-RPC.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result
        """
        client = await self._get_client()

        # MCP JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        response = await client.post(self.api_url, json=payload)
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise RuntimeError(f"SimpleMem error: {result['error']}")

        return result.get("result", {})

    async def store_memory(
        self,
        content: str,
        speaker: str = "system",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Store a memory/dialogue entry.

        Args:
            content: The memory content to store
            speaker: Who/what generated this memory (e.g., "doctor", "system")
            timestamp: ISO 8601 timestamp (defaults to now)
            metadata: Additional metadata (patient_id, visit_id, etc.)

        Returns:
            Storage confirmation
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Build the memory entry with metadata embedded in content for searchability
        memory_content = content
        if metadata:
            # Embed key metadata in content for better retrieval
            meta_str = " | ".join(f"{k}:{v}" for k, v in metadata.items())
            memory_content = f"[{meta_str}] {content}"

        return await self._call_tool(
            "add_dialogue",
            {
                "speaker": speaker,
                "content": memory_content,
                "timestamp": timestamp,
            },
        )

    async def search_memories(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search memories using semantic + lexical search.

        Args:
            query: Search query (natural language)
            limit: Maximum results to return

        Returns:
            Matching memories
        """
        return await self._call_tool(
            "search",
            {
                "query": query,
                "limit": limit,
            },
        )

    async def get_recent_memories(
        self,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get recent memories.

        Args:
            limit: Maximum results

        Returns:
            Recent memories
        """
        return await self._call_tool(
            "get_recent",
            {
                "limit": limit,
            },
        )

    # ===================
    # Clinical memory helpers
    # ===================

    async def store_patient_encounter(
        self,
        patient_id: int,
        patient_name: str,
        encounter_summary: str,
        visit_date: str,
        doctor_name: str | None = None,
        chief_complaint: str | None = None,
        diagnosis: list[str] | None = None,
        plan: str | None = None,
    ) -> dict[str, Any]:
        """Store a clinical encounter summary for future reference.

        Args:
            patient_id: DrChrono patient ID
            patient_name: Patient's full name
            encounter_summary: Summary of the encounter
            visit_date: Date of visit (YYYY-MM-DD)
            doctor_name: Treating physician
            chief_complaint: Chief complaint
            diagnosis: List of diagnoses
            plan: Treatment plan

        Returns:
            Storage confirmation
        """
        # Build comprehensive memory entry
        parts = [f"Patient Encounter: {patient_name} (ID: {patient_id})"]
        parts.append(f"Date: {visit_date}")

        if doctor_name:
            parts.append(f"Provider: {doctor_name}")
        if chief_complaint:
            parts.append(f"Chief Complaint: {chief_complaint}")
        if diagnosis:
            parts.append(f"Diagnosis: {', '.join(diagnosis)}")
        if plan:
            parts.append(f"Plan: {plan}")

        parts.append(f"Summary: {encounter_summary}")

        content = "\n".join(parts)

        return await self.store_memory(
            content=content,
            speaker="clinical_system",
            metadata={
                "patient_id": patient_id,
                "visit_date": visit_date,
                "type": "encounter",
            },
        )

    async def store_clinical_alert(
        self,
        patient_id: int,
        patient_name: str,
        alert_type: str,
        alert_content: str,
        severity: str = "info",
    ) -> dict[str, Any]:
        """Store a clinical alert/flag for a patient.

        Args:
            patient_id: DrChrono patient ID
            patient_name: Patient name
            alert_type: Type of alert (allergy, drug_interaction, lab_critical, etc.)
            alert_content: Alert details
            severity: info, warning, or critical

        Returns:
            Storage confirmation
        """
        content = (
            f"CLINICAL ALERT [{severity.upper()}] - {patient_name} (ID: {patient_id})\n"
            f"Type: {alert_type}\n"
            f"Details: {alert_content}"
        )

        return await self.store_memory(
            content=content,
            speaker="alert_system",
            metadata={
                "patient_id": patient_id,
                "alert_type": alert_type,
                "severity": severity,
                "type": "alert",
            },
        )

    async def get_patient_memories(
        self,
        patient_id: int,
        patient_name: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get all memories related to a specific patient.

        Args:
            patient_id: DrChrono patient ID
            patient_name: Patient name for semantic search
            limit: Maximum results

        Returns:
            Patient-related memories
        """
        # Search by both ID and name for comprehensive results
        query = f"patient_id:{patient_id} {patient_name}"
        return await self.search_memories(query, limit)
