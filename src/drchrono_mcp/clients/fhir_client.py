"""FHIR R4 client for DrChrono via ConnectEHR/Dynamic Health IT."""

from typing import Any

import httpx


class FHIRClient:
    """Async FHIR R4 client for DrChrono ConnectEHR integration.

    DrChrono uses ConnectEHR (Dynamic Health IT) for FHIR compliance.
    This client handles SMART on FHIR authentication and standard
    FHIR R4 resource operations.

    Note: FHIR access requires separate ConnectEHR credentials configured
    at the practice level. See DrChrono's FHIR setup documentation.
    """

    def __init__(
        self,
        base_url: str,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """Initialize FHIR client.

        Args:
            base_url: FHIR server base URL (e.g., https://practice.dynamicfhir.com/fhir/r4)
            client_id: SMART on FHIR client ID (optional for patient-level auth)
            client_secret: SMART on FHIR client secret
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if FHIR credentials are configured."""
        return bool(self.base_url and self.client_id)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            }
            if self._access_token:
                headers["Authorization"] = f"Bearer {self._access_token}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def authenticate(self, username: str, password: str) -> str:
        """Authenticate with ConnectEHR credentials.

        For provider-level access, uses username/password from ConnectEHR setup.

        Args:
            username: ConnectEHR username
            password: ConnectEHR password

        Returns:
            Access token
        """
        # ConnectEHR uses OAuth2 password grant for provider access
        async with httpx.AsyncClient() as client:
            # Token endpoint is typically at /oauth2/token
            token_url = f"{self.base_url}/oauth2/token"

            response = await client.post(
                token_url,
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

        self._access_token = data["access_token"]
        return self._access_token

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make FHIR request."""
        client = await self._get_client()

        response = await client.request(
            method,
            path,
            params=params,
            json=json,
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {}

        return response.json()

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """GET request."""
        return await self._request("GET", path, params=params)

    async def post(
        self, path: str, json: dict[str, Any]
    ) -> dict[str, Any]:
        """POST request."""
        return await self._request("POST", path, json=json)

    # ===================
    # FHIR Operations
    # ===================

    async def get_capability_statement(self) -> dict[str, Any]:
        """Get server capability statement (metadata).

        Returns supported resources, operations, and search parameters.
        """
        return await self.get("/metadata")

    async def get_resource(
        self, resource_type: str, resource_id: str
    ) -> dict[str, Any]:
        """Get a specific FHIR resource by ID.

        Args:
            resource_type: FHIR resource type (Patient, Observation, etc.)
            resource_id: Resource ID

        Returns:
            FHIR resource
        """
        return await self.get(f"/{resource_type}/{resource_id}")

    async def search(
        self,
        resource_type: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Search for FHIR resources.

        Args:
            resource_type: FHIR resource type to search
            params: Search parameters (FHIR search syntax)

        Returns:
            FHIR Bundle with search results
        """
        return await self.get(f"/{resource_type}", params)

    async def get_patient(self, patient_id: str) -> dict[str, Any]:
        """Get Patient resource."""
        return await self.get_resource("Patient", patient_id)

    async def search_patients(
        self,
        name: str | None = None,
        birthdate: str | None = None,
        identifier: str | None = None,
    ) -> dict[str, Any]:
        """Search for patients.

        Args:
            name: Patient name (partial match)
            birthdate: Date of birth (YYYY-MM-DD)
            identifier: Patient identifier

        Returns:
            Bundle of matching Patient resources
        """
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if birthdate:
            params["birthdate"] = birthdate
        if identifier:
            params["identifier"] = identifier

        return await self.search("Patient", params)

    async def get_observations(
        self,
        patient_id: str,
        category: str | None = None,
        code: str | None = None,
    ) -> dict[str, Any]:
        """Get Observation resources for a patient.

        Args:
            patient_id: Patient resource ID
            category: Observation category (vital-signs, laboratory, etc.)
            code: LOINC or other code

        Returns:
            Bundle of Observation resources
        """
        params: dict[str, Any] = {"patient": patient_id}
        if category:
            params["category"] = category
        if code:
            params["code"] = code

        return await self.search("Observation", params)

    async def get_conditions(self, patient_id: str) -> dict[str, Any]:
        """Get Condition resources for a patient."""
        return await self.search("Condition", {"patient": patient_id})

    async def get_medications(self, patient_id: str) -> dict[str, Any]:
        """Get MedicationRequest resources for a patient."""
        return await self.search("MedicationRequest", {"patient": patient_id})

    async def get_allergies(self, patient_id: str) -> dict[str, Any]:
        """Get AllergyIntolerance resources for a patient."""
        return await self.search("AllergyIntolerance", {"patient": patient_id})

    async def get_immunizations(self, patient_id: str) -> dict[str, Any]:
        """Get Immunization resources for a patient."""
        return await self.search("Immunization", {"patient": patient_id})

    async def get_diagnostic_reports(self, patient_id: str) -> dict[str, Any]:
        """Get DiagnosticReport resources (lab results, imaging)."""
        return await self.search("DiagnosticReport", {"patient": patient_id})

    async def get_procedures(self, patient_id: str) -> dict[str, Any]:
        """Get Procedure resources for a patient."""
        return await self.search("Procedure", {"patient": patient_id})

    async def get_encounters(self, patient_id: str) -> dict[str, Any]:
        """Get Encounter resources for a patient."""
        return await self.search("Encounter", {"patient": patient_id})

    async def get_document_references(self, patient_id: str) -> dict[str, Any]:
        """Get DocumentReference resources for a patient."""
        return await self.search("DocumentReference", {"patient": patient_id})

    # ===================
    # Convenience methods
    # ===================

    async def get_patient_everything(self, patient_id: str) -> dict[str, Any]:
        """Get all data for a patient using $everything operation.

        This is a FHIR operation that returns all resources related to
        a patient in a single Bundle.

        Note: Not all servers support this operation.
        """
        return await self.get(f"/Patient/{patient_id}/$everything")
