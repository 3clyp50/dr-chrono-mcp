"""Clinical tools: patients, appointments, clinical notes, health records."""

from typing import Literal

from mcp.server import Server

from drchrono_mcp.clients.rest_client import DrChronoClient
from drchrono_mcp.models.types import AppointmentStatus, Gender, NoteFormat


def register_clinical_tools(server: Server, client: DrChronoClient) -> None:
    """Register clinical tools with MCP server.

    Args:
        server: MCP Server instance
        client: DrChrono REST API client
    """

    # ===================
    # Patient Tools
    # ===================

    @server.tool()
    async def drchrono_get_patient_summary(
        patient_id: int | None = None,
        email: str | None = None,
        name: str | None = None,
    ) -> dict:
        """Get a patient's summary including demographics, insurance, and recent appointments.

        Use this when you need comprehensive patient information in one call.
        Provide ONE of: patient_id, email, or name.

        Args:
            patient_id: DrChrono patient ID (most reliable)
            email: Patient email address (exact match)
            name: Patient name to search (partial match, returns first match)

        Returns:
            Patient summary with demographics, insurance info, and recent appointments
        """
        # Find patient by identifier
        if patient_id:
            patient = await client.get_patient(patient_id, verbose=True)
        elif email:
            results = await client.search_patients(email=email, limit=1)
            if not results["results"]:
                return {"error": f"No patient found with email: {email}"}
            patient = await client.get_patient(results["results"][0]["id"], verbose=True)
        elif name:
            # Try to parse as "First Last"
            parts = name.split(maxsplit=1)
            first = parts[0] if parts else None
            last = parts[1] if len(parts) > 1 else None
            results = await client.search_patients(first_name=first, last_name=last, limit=1)
            if not results["results"]:
                return {"error": f"No patient found matching name: {name}"}
            patient = await client.get_patient(results["results"][0]["id"], verbose=True)
        else:
            return {"error": "Provide patient_id, email, or name to identify the patient"}

        # Get recent appointments
        appointments = await client.get_appointments(patient_id=patient["id"], limit=5)

        # Build summary
        return {
            "id": patient["id"],
            "first_name": patient.get("first_name"),
            "last_name": patient.get("last_name"),
            "date_of_birth": patient.get("date_of_birth"),
            "gender": patient.get("gender"),
            "email": patient.get("email"),
            "cell_phone": patient.get("cell_phone"),
            "home_phone": patient.get("home_phone"),
            "address": patient.get("address"),
            "city": patient.get("city"),
            "state": patient.get("state"),
            "zip_code": patient.get("zip_code"),
            "primary_insurance": patient.get("primary_insurance"),
            "secondary_insurance": patient.get("secondary_insurance"),
            "primary_care_physician": patient.get("primary_care_physician"),
            "recent_appointments": [
                {
                    "id": apt["id"],
                    "scheduled_time": apt.get("scheduled_time"),
                    "status": apt.get("status"),
                    "reason": apt.get("reason"),
                    "doctor": apt.get("doctor"),
                }
                for apt in appointments.get("results", [])
            ],
        }

    @server.tool()
    async def drchrono_search_patients(
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        email: str | None = None,
        limit: int = 25,
    ) -> dict:
        """Search for patients by criteria.

        Provide any combination of search parameters. Results are patients
        matching ALL provided criteria.

        Args:
            first_name: First name (partial match)
            last_name: Last name (partial match)
            date_of_birth: Date of birth in YYYY-MM-DD format (exact match)
            email: Email address (exact match)
            limit: Maximum results to return (default 25, max 250)

        Returns:
            List of matching patients with basic info
        """
        if not any([first_name, last_name, date_of_birth, email]):
            return {"error": "Provide at least one search criteria"}

        results = await client.search_patients(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            limit=min(limit, 250),
        )

        return {
            "patients": [
                {
                    "id": p["id"],
                    "first_name": p.get("first_name"),
                    "last_name": p.get("last_name"),
                    "date_of_birth": p.get("date_of_birth"),
                    "email": p.get("email"),
                    "cell_phone": p.get("cell_phone"),
                }
                for p in results["results"]
            ],
            "total_count": results["total_count"],
            "has_more": results["has_more"],
        }

    @server.tool()
    async def drchrono_create_patient(
        first_name: str,
        last_name: str,
        date_of_birth: str,
        doctor_id: int,
        email: str | None = None,
        cell_phone: str | None = None,
        gender: Gender | None = None,
    ) -> dict:
        """Create a new patient record.

        Args:
            first_name: Patient's first name (required)
            last_name: Patient's last name (required)
            date_of_birth: Date of birth in YYYY-MM-DD format (required)
            doctor_id: Primary doctor ID for this patient (required)
            email: Email address
            cell_phone: Cell phone number (format: XXX-XXX-XXXX)
            gender: Gender - "Male", "Female", "Other", or "UNK"

        Returns:
            Created patient record with ID
        """
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "doctor": doctor_id,
        }

        if email:
            data["email"] = email
        if cell_phone:
            data["cell_phone"] = cell_phone
        if gender:
            data["gender"] = gender

        result = await client.create_patient(data)

        return {
            "success": True,
            "patient_id": result.get("id"),
            "message": f"Patient {first_name} {last_name} created successfully",
            "patient": result,
        }

    @server.tool()
    async def drchrono_update_patient(
        patient_id: int,
        email: str | None = None,
        cell_phone: str | None = None,
        home_phone: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
    ) -> dict:
        """Update patient demographics.

        Only provided fields will be updated. Other fields remain unchanged.

        Args:
            patient_id: DrChrono patient ID (required)
            email: New email address
            cell_phone: New cell phone (format: XXX-XXX-XXXX)
            home_phone: New home phone
            address: Street address
            city: City
            state: State (2-letter code)
            zip_code: ZIP code

        Returns:
            Updated patient record
        """
        data = {}
        if email is not None:
            data["email"] = email
        if cell_phone is not None:
            data["cell_phone"] = cell_phone
        if home_phone is not None:
            data["home_phone"] = home_phone
        if address is not None:
            data["address"] = address
        if city is not None:
            data["city"] = city
        if state is not None:
            data["state"] = state
        if zip_code is not None:
            data["zip_code"] = zip_code

        if not data:
            return {"error": "No fields provided to update"}

        await client.update_patient(patient_id, data)

        return {
            "success": True,
            "patient_id": patient_id,
            "message": "Patient updated successfully",
            "updated_fields": list(data.keys()),
        }

    # ===================
    # Appointment Tools
    # ===================

    @server.tool()
    async def drchrono_get_appointments(
        date: str | None = None,
        since: str | None = None,
        patient_id: int | None = None,
        doctor_id: int | None = None,
        status: AppointmentStatus | None = None,
        limit: int = 50,
    ) -> dict:
        """Get appointments with optional filtering.

        Use date for a specific day, or since for all appointments since a date.

        Args:
            date: Specific date in YYYY-MM-DD format
            since: All appointments since this date (YYYY-MM-DD)
            patient_id: Filter by patient
            doctor_id: Filter by doctor
            status: Filter by status - "Confirmed", "Checked In", "Complete", "Cancelled", etc.
            limit: Maximum results (default 50, max 250)

        Returns:
            List of appointments matching criteria
        """
        results = await client.get_appointments(
            date=date,
            since=since,
            patient_id=patient_id,
            doctor_id=doctor_id,
            status=status if status else None,
            limit=min(limit, 250),
        )

        return {
            "appointments": [
                {
                    "id": apt["id"],
                    "patient": apt.get("patient"),
                    "doctor": apt.get("doctor"),
                    "scheduled_time": apt.get("scheduled_time"),
                    "duration": apt.get("duration"),
                    "status": apt.get("status"),
                    "reason": apt.get("reason"),
                    "office": apt.get("office"),
                    "exam_room": apt.get("exam_room"),
                }
                for apt in results["results"]
            ],
            "total_count": results["total_count"],
            "has_more": results["has_more"],
        }

    @server.tool()
    async def drchrono_create_appointment(
        patient_id: int,
        doctor_id: int,
        office_id: int,
        scheduled_time: str,
        duration: int = 30,
        reason: str | None = None,
        exam_room: int | None = None,
    ) -> dict:
        """Schedule a new appointment.

        Args:
            patient_id: Patient ID (required)
            doctor_id: Doctor ID (required)
            office_id: Office/location ID (required)
            scheduled_time: Date/time in ISO format YYYY-MM-DDTHH:MM:SS (required)
            duration: Duration in minutes (default 30)
            reason: Reason for visit
            exam_room: Exam room number

        Returns:
            Created appointment with ID
        """
        data = {
            "patient": patient_id,
            "doctor": doctor_id,
            "office": office_id,
            "scheduled_time": scheduled_time,
            "duration": duration,
        }

        if reason:
            data["reason"] = reason
        if exam_room:
            data["exam_room"] = exam_room

        result = await client.create_appointment(data)

        return {
            "success": True,
            "appointment_id": result.get("id"),
            "scheduled_time": scheduled_time,
            "message": "Appointment scheduled successfully",
        }

    @server.tool()
    async def drchrono_update_appointment(
        appointment_id: int,
        status: Literal[
            "Confirmed", "Cancelled", "No Show", "Rescheduled", "Arrived", "Complete"
        ] | None = None,
        scheduled_time: str | None = None,
        duration: int | None = None,
        reason: str | None = None,
    ) -> dict:
        """Update or cancel an appointment.

        Only provided fields will be updated.

        Args:
            appointment_id: Appointment ID (required)
            status: New status - "Confirmed", "Cancelled", "No Show", "Rescheduled", etc.
            scheduled_time: New date/time in ISO format (for rescheduling)
            duration: New duration in minutes
            reason: Updated reason for visit

        Returns:
            Updated appointment confirmation
        """
        data = {}
        if status is not None:
            data["status"] = status
        if scheduled_time is not None:
            data["scheduled_time"] = scheduled_time
        if duration is not None:
            data["duration"] = duration
        if reason is not None:
            data["reason"] = reason

        if not data:
            return {"error": "No fields provided to update"}

        await client.update_appointment(appointment_id, data)

        return {
            "success": True,
            "appointment_id": appointment_id,
            "updated_fields": list(data.keys()),
            "message": f"Appointment {appointment_id} updated",
        }

    # ===================
    # Clinical Note Tools
    # ===================

    @server.tool()
    async def drchrono_get_clinical_note(
        appointment_id: int,
        format: NoteFormat = "raw",
    ) -> dict:
        """Get clinical note for an appointment.

        Args:
            appointment_id: Appointment ID (required)
            format: "raw" for editable data, "pdf_url" for signed PDF link

        Returns:
            Clinical note content or PDF URL
        """
        results = await client.get_clinical_note(appointment_id)

        if not results.get("results"):
            return {
                "appointment_id": appointment_id,
                "has_note": False,
                "message": "No clinical note found for this appointment",
            }

        note = results["results"][0]

        if format == "pdf_url":
            # Get PDF URL from appointment
            apt = await client.get_appointment(appointment_id)
            pdf_url = apt.get("clinical_note", {}).get("pdf")
            return {
                "appointment_id": appointment_id,
                "has_note": True,
                "pdf_url": pdf_url,
                "note_id": note.get("id"),
                "locked": note.get("locked", False),
            }

        return {
            "appointment_id": appointment_id,
            "has_note": True,
            "note_id": note.get("id"),
            "locked": note.get("locked", False),
            "chief_complaint": note.get("chief_complaint"),
            "history_of_present_illness": note.get("history_of_present_illness"),
            "review_of_systems": note.get("review_of_systems"),
            "physical_examination": note.get("physical_examination"),
            "assessment": note.get("assessment"),
            "plan": note.get("plan"),
        }

    @server.tool()
    async def drchrono_add_clinical_note(
        appointment_id: int,
        chief_complaint: str | None = None,
        history_of_present_illness: str | None = None,
        plan: str | None = None,
        notes: str | None = None,
    ) -> dict:
        """Add or update clinical note for an appointment.

        Only provided fields will be updated. Note must not be locked.

        Args:
            appointment_id: Appointment ID (required)
            chief_complaint: Chief complaint text
            history_of_present_illness: HPI narrative
            plan: Treatment plan
            notes: Additional notes

        Returns:
            Updated note confirmation
        """
        # First get existing note
        results = await client.get_clinical_note(appointment_id)

        if not results.get("results"):
            return {
                "error": "No clinical note exists for this appointment. "
                "Notes are created automatically when appointment is created.",
            }

        note = results["results"][0]

        if note.get("locked"):
            return {
                "error": "Clinical note is locked and cannot be edited. "
                "Locked notes have been signed and finalized.",
            }

        data = {}
        if chief_complaint is not None:
            data["chief_complaint"] = chief_complaint
        if history_of_present_illness is not None:
            data["history_of_present_illness"] = history_of_present_illness
        if plan is not None:
            data["plan"] = plan
        if notes is not None:
            data["notes"] = notes

        if not data:
            return {"error": "No fields provided to update"}

        await client.update_clinical_note(note["id"], data)

        return {
            "success": True,
            "note_id": note["id"],
            "appointment_id": appointment_id,
            "updated_fields": list(data.keys()),
            "message": "Clinical note updated successfully",
        }

    # ===================
    # Health Record Tool
    # ===================

    @server.tool()
    async def drchrono_get_patient_health_record(patient_id: int) -> dict:
        """Get complete health record for a patient.

        Includes medications, allergies, problems/conditions, and vaccines.
        This consolidates multiple API calls into one comprehensive response.

        Args:
            patient_id: Patient ID (required)

        Returns:
            Complete health record with all clinical data
        """
        # Fetch all health data in parallel
        import asyncio

        meds, allergies, problems, vaccines = await asyncio.gather(
            client.get_medications(patient_id),
            client.get_allergies(patient_id),
            client.get_problems(patient_id),
            client.get_vaccines(patient_id),
        )

        return {
            "patient_id": patient_id,
            "medications": [
                {
                    "id": m["id"],
                    "name": m.get("name"),
                    "dose": m.get("dose"),
                    "frequency": m.get("frequency"),
                    "status": m.get("status"),
                    "prescribed_date": m.get("date_prescribed"),
                }
                for m in meds.get("results", [])
            ],
            "allergies": [
                {
                    "id": a["id"],
                    "name": a.get("name"),
                    "reaction": a.get("reaction"),
                    "status": a.get("status"),
                }
                for a in allergies.get("results", [])
            ],
            "problems": [
                {
                    "id": p["id"],
                    "name": p.get("name"),
                    "icd_code": p.get("icd_code"),
                    "status": p.get("status"),
                    "date_diagnosis": p.get("date_diagnosis"),
                }
                for p in problems.get("results", [])
            ],
            "vaccines": [
                {
                    "id": v["id"],
                    "name": v.get("name"),
                    "cvx_code": v.get("cvx_code"),
                    "administered_date": v.get("administered_date"),
                }
                for v in vaccines.get("results", [])
            ],
        }
