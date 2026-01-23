"""Type definitions and Pydantic models for DrChrono MCP server."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Literal types for constrained parameters (prevents LLM hallucination)
Gender = Literal["Male", "Female", "Other", "UNK"]

AppointmentStatus = Literal[
    "",  # Any status
    "Arrived",
    "Checked In",
    "Checked In Online",
    "In Room",
    "In Session",
    "Complete",
    "Confirmed",
    "Not Confirmed",
    "Rescheduled",
    "Cancelled",
    "No Show",
]

InsuranceType = Literal["primary", "secondary", "tertiary"]

DocumentType = Literal["lab", "imaging", "other"]

NoteFormat = Literal["raw", "pdf_url"]

FHIRResourceType = Literal[
    "Patient",
    "Observation",
    "Condition",
    "MedicationRequest",
    "AllergyIntolerance",
    "Immunization",
    "DiagnosticReport",
    "Procedure",
    "Encounter",
    "DocumentReference",
]


class TokenData(BaseModel):
    """OAuth token storage model."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    scope: str = ""

    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)."""
        from datetime import timedelta

        return datetime.now() >= (self.expires_at - timedelta(minutes=5))


class PatientSummary(BaseModel):
    """Simplified patient data for tool responses."""

    id: int
    first_name: str
    last_name: str
    date_of_birth: str
    email: str | None = None
    cell_phone: str | None = None
    gender: str | None = None
    primary_insurance: str | None = None
    recent_appointments: list[dict] = Field(default_factory=list)


class AppointmentSummary(BaseModel):
    """Simplified appointment data for tool responses."""

    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    scheduled_time: str
    duration: int
    status: str
    reason: str | None = None
    office: str | None = None


class HealthRecord(BaseModel):
    """Combined health record data."""

    patient_id: int
    medications: list[dict] = Field(default_factory=list)
    allergies: list[dict] = Field(default_factory=list)
    problems: list[dict] = Field(default_factory=list)
    vaccines: list[dict] = Field(default_factory=list)


class BillingSummary(BaseModel):
    """Billing overview for a patient."""

    patient_id: int
    total_charges: float = 0.0
    total_payments: float = 0.0
    balance: float = 0.0
    line_items: list[dict] = Field(default_factory=list)
    recent_transactions: list[dict] = Field(default_factory=list)


class PaginatedResponse(BaseModel):
    """Standard paginated response wrapper."""

    results: list[dict]
    total_count: int
    has_more: bool
    next_offset: int | None = None
