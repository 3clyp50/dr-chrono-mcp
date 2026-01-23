"""DrChrono REST API client with rate limiting and bulk API support."""

import asyncio
from typing import Any

import httpx

from drchrono_mcp.auth.oauth import OAuthManager

API_BASE = "https://app.drchrono.com/api"


class DrChronoClient:
    """Async HTTP client for DrChrono REST API.

    Features:
    - Automatic token refresh via OAuthManager
    - Rate limit handling with exponential backoff
    - Bulk API support for large data retrieval
    - Pagination helpers
    """

    def __init__(self, oauth: OAuthManager):
        """Initialize client with OAuth manager.

        Args:
            oauth: Configured OAuthManager for token handling
        """
        self.oauth = oauth
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        token = await self.oauth.get_access_token()
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=API_BASE,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        else:
            # Update token in case it was refreshed
            self._client.headers["Authorization"] = f"Bearer {token}"
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make API request with rate limit handling.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (without /api prefix)
            params: Query parameters
            json: JSON body for POST/PATCH
            max_retries: Max retry attempts for rate limits

        Returns:
            Response JSON as dict
        """
        client = await self._get_client()

        for attempt in range(max_retries):
            try:
                response = await client.request(
                    method,
                    endpoint,
                    params=params,
                    json=json,
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()

                if response.status_code == 204:  # No content
                    return {}

                return response.json()

            except httpx.HTTPStatusError as e:
                if attempt == max_retries - 1:
                    raise
                if e.response.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise

        raise RuntimeError("Max retries exceeded")

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST request."""
        return await self._request("POST", endpoint, params=params, json=json)

    async def patch(
        self, endpoint: str, json: dict[str, Any]
    ) -> dict[str, Any]:
        """PATCH request for updates."""
        return await self._request("PATCH", endpoint, json=json)

    async def delete(self, endpoint: str) -> dict[str, Any]:
        """DELETE request."""
        return await self._request("DELETE", endpoint)

    # ===================
    # Convenience methods
    # ===================

    async def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get paginated results with metadata.

        Returns dict with:
        - results: List of items
        - total_count: Total available (if known)
        - has_more: Whether more pages exist
        - next_offset: Offset for next page
        """
        params = params or {}
        params["page_size"] = min(limit, 250)  # DrChrono max is 250

        response = await self.get(endpoint, params)

        results = response.get("results", [])
        next_url = response.get("next")

        return {
            "results": results[:limit],
            "total_count": len(results),
            "has_more": next_url is not None,
            "next_offset": len(results) if next_url else None,
        }

    async def bulk_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        page_size: int = 1000,
    ) -> dict[str, Any]:
        """Use bulk API for large result sets.

        DrChrono bulk APIs:
        1. POST to endpoint_list to start async job
        2. GET with uuid to poll for results

        Args:
            endpoint: Base endpoint name (e.g., "appointments")
            params: Filter parameters
            page_size: Results per page (max 1000)

        Returns:
            Paginated results
        """
        list_endpoint = f"/{endpoint}_list"
        params = params or {}
        params["page_size"] = min(page_size, 1000)

        # Start bulk job
        start_response = await self.post(list_endpoint, params=params)
        uuid = start_response.get("uuid")

        if not uuid:
            # Fallback to regular pagination
            return await self.get_paginated(f"/{endpoint}", params)

        # Poll for completion
        for _ in range(60):  # Max 5 minutes
            result = await self.get(list_endpoint, {"uuid": uuid})

            if result.get("status") == "Complete":
                pagination = result.get("pagination", {})
                return {
                    "results": result.get("results", []),
                    "total_count": pagination.get("count", 0),
                    "has_more": pagination.get("page", 1) < pagination.get("pages", 1),
                    "next_offset": (
                        pagination.get("page_size") if pagination.get("pages", 1) > 1 else None
                    ),
                }

            await asyncio.sleep(5)

        raise TimeoutError("Bulk request timed out")

    # ===================
    # Resource methods
    # ===================

    async def get_patient(self, patient_id: int, verbose: bool = False) -> dict[str, Any]:
        """Get patient by ID."""
        params = {"verbose": "true"} if verbose else None
        return await self.get(f"/patients/{patient_id}", params)

    async def search_patients(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        email: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Search patients by criteria."""
        params: dict[str, Any] = {}
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if date_of_birth:
            params["date_of_birth"] = date_of_birth
        if email:
            params["email"] = email

        return await self.get_paginated("/patients", params, limit)

    async def create_patient(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create new patient."""
        return await self.post("/patients", json=data)

    async def update_patient(self, patient_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update patient."""
        return await self.patch(f"/patients/{patient_id}", json=data)

    async def get_appointments(
        self,
        date: str | None = None,
        since: str | None = None,
        patient_id: int | None = None,
        doctor_id: int | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get appointments with filters."""
        params: dict[str, Any] = {}
        if date:
            params["date"] = date
        if since:
            params["since"] = since
        if patient_id:
            params["patient"] = patient_id
        if doctor_id:
            params["doctor"] = doctor_id
        if status:
            params["status"] = status

        return await self.get_paginated("/appointments", params, limit)

    async def get_appointment(self, appointment_id: int) -> dict[str, Any]:
        """Get single appointment."""
        return await self.get(f"/appointments/{appointment_id}")

    async def create_appointment(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create appointment."""
        return await self.post("/appointments", json=data)

    async def update_appointment(
        self, appointment_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update appointment."""
        return await self.patch(f"/appointments/{appointment_id}", json=data)

    async def get_clinical_note(self, appointment_id: int) -> dict[str, Any]:
        """Get clinical note for appointment."""
        return await self.get("/clinical_notes", {"appointment": appointment_id})

    async def update_clinical_note(
        self, clinical_note_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update clinical note."""
        return await self.patch(f"/clinical_notes/{clinical_note_id}", json=data)

    async def get_medications(self, patient_id: int) -> dict[str, Any]:
        """Get patient medications."""
        return await self.get_paginated("/medications", {"patient": patient_id})

    async def get_allergies(self, patient_id: int) -> dict[str, Any]:
        """Get patient allergies."""
        return await self.get_paginated("/allergies", {"patient": patient_id})

    async def get_problems(self, patient_id: int) -> dict[str, Any]:
        """Get patient problems/conditions."""
        return await self.get_paginated("/problems", {"patient": patient_id})

    async def get_vaccines(self, patient_id: int) -> dict[str, Any]:
        """Get patient vaccine records."""
        return await self.get_paginated("/vaccine_records", {"patient": patient_id})

    async def get_lab_results(
        self, patient_id: int, since: str | None = None, limit: int = 25
    ) -> dict[str, Any]:
        """Get patient lab results."""
        params: dict[str, Any] = {"patient": patient_id}
        if since:
            params["since"] = since
        return await self.get_paginated("/patient_lab_results", params, limit)

    async def get_documents(
        self, patient_id: int, limit: int = 25
    ) -> dict[str, Any]:
        """Get patient documents."""
        return await self.get_paginated("/documents", {"patient": patient_id}, limit)

    async def get_ccda(self, patient_id: int) -> dict[str, Any]:
        """Get CCDA export for patient."""
        return await self.get(f"/patients/{patient_id}/ccda")

    async def check_eligibility(
        self, patient_id: int, insurance_type: str = "primary"
    ) -> dict[str, Any]:
        """Check insurance eligibility."""
        return await self.get_paginated(
            "/eligibility_checks",
            {"patient": patient_id, "insurance_type": insurance_type},
        )

    async def get_line_items(
        self, patient_id: int | None = None, since: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        """Get billing line items."""
        params: dict[str, Any] = {}
        if patient_id:
            params["patient"] = patient_id
        if since:
            params["since"] = since
        return await self.get_paginated("/line_items", params, limit)

    async def get_transactions(
        self, since: str, patient_id: int | None = None, limit: int = 100
    ) -> dict[str, Any]:
        """Get payment transactions."""
        params: dict[str, Any] = {"since": since}
        if patient_id:
            params["patient"] = patient_id
        return await self.get_paginated("/transactions", params, limit)

    async def get_doctors(self) -> dict[str, Any]:
        """Get doctors for practice."""
        return await self.get_paginated("/doctors")

    async def get_offices(self) -> dict[str, Any]:
        """Get offices for practice."""
        return await self.get_paginated("/offices")
