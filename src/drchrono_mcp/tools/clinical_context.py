"""Comprehensive clinical context tool for patient visits.

This module provides tools that pull ALL clinically relevant information
about a patient, presenting it in a format optimized for clinical decision-making.
"""

import asyncio
from datetime import datetime, timedelta

from mcp.server import Server

from drchrono_mcp.clients.rest_client import DrChronoClient
from drchrono_mcp.clients.simplemem_client import SimpleMemClient
from drchrono_mcp.ui import ClinicalChartBuilder, ClinicalDisplayBuilder


def register_clinical_context_tools(
    server: Server,
    client: DrChronoClient,
    memory_client: SimpleMemClient | None,
) -> None:
    """Register comprehensive clinical context tools.

    Args:
        server: MCP Server instance
        client: DrChrono REST API client
        memory_client: SimpleMem client for persistent memory (optional)
    """

    @server.tool()
    async def drchrono_get_clinical_context(
        patient_id: int | None = None,
        appointment_id: int | None = None,
        include_billing: bool = False,
    ) -> dict:
        """Get COMPLETE clinical context for a patient visit.

        This is the primary tool for doctors to get ALL clinically relevant
        information about a patient in one call. Returns:

        - Patient demographics and contact info
        - Current visit/appointment details
        - Active medications with dosages
        - Known allergies (CRITICAL for prescribing)
        - Active problems/conditions with ICD codes
        - Immunization history
        - Recent lab results (last 90 days)
        - Recent clinical notes (last 3 visits)
        - Insurance/eligibility (if include_billing=True)
        - Past encounter memories from clinical memory system
        - Clinical alerts and flags

        Use this at the START of any patient interaction.

        Args:
            patient_id: Patient ID (provide this OR appointment_id)
            appointment_id: Current appointment ID (will auto-fetch patient)
            include_billing: Include insurance/billing info (default False)

        Returns:
            Comprehensive clinical context for the patient
        """
        # Resolve patient from appointment if needed
        if appointment_id and not patient_id:
            apt = await client.get_appointment(appointment_id)
            patient_id = apt.get("patient")
            if not patient_id:
                return {"error": f"No patient found for appointment {appointment_id}"}

        if not patient_id:
            return {"error": "Provide patient_id or appointment_id"}

        # Fetch all data in parallel for speed
        tasks = {
            "patient": client.get_patient(patient_id, verbose=True),
            "medications": client.get_medications(patient_id),
            "allergies": client.get_allergies(patient_id),
            "problems": client.get_problems(patient_id),
            "vaccines": client.get_vaccines(patient_id),
            "recent_appointments": client.get_appointments(
                patient_id=patient_id,
                since=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                limit=10,
            ),
        }

        # Add lab results (last 90 days)
        since_90_days = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        tasks["lab_results"] = client.get_lab_results(
            patient_id, since=since_90_days, limit=20
        )

        # Add documents (recent)
        tasks["documents"] = client.get_documents(patient_id, limit=10)

        # Add billing if requested
        if include_billing:
            tasks["eligibility"] = client.check_eligibility(patient_id, "primary")

        # Execute all in parallel
        results = {}
        task_list = list(tasks.items())
        responses = await asyncio.gather(
            *[t[1] for t in task_list],
            return_exceptions=True,
        )
        for (key, _), response in zip(task_list, responses, strict=True):
            if isinstance(response, Exception):
                results[key] = {"error": str(response)}
            else:
                results[key] = response

        patient = results.get("patient", {})

        # Build clinical context response
        context = {
            "retrieved_at": datetime.now().isoformat(),
            "patient_id": patient_id,
            # === DEMOGRAPHICS ===
            "demographics": {
                "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
                "date_of_birth": patient.get("date_of_birth"),
                "age": _calculate_age(patient.get("date_of_birth")),
                "gender": patient.get("gender"),
                "preferred_language": patient.get("preferred_language"),
                "race": patient.get("race"),
                "ethnicity": patient.get("ethnicity"),
            },
            "contact": {
                "cell_phone": patient.get("cell_phone"),
                "home_phone": patient.get("home_phone"),
                "email": patient.get("email"),
                "address": _format_address(patient),
                "emergency_contact": patient.get("emergency_contact_name"),
                "emergency_phone": patient.get("emergency_contact_phone"),
            },
            # === CRITICAL CLINICAL INFO ===
            "allergies": _format_allergies(results.get("allergies", {})),
            "active_medications": _format_medications(results.get("medications", {})),
            "active_problems": _format_problems(results.get("problems", {})),
            # === PREVENTIVE CARE ===
            "immunizations": _format_vaccines(results.get("vaccines", {})),
            # === RECENT CLINICAL DATA ===
            "recent_labs": _format_labs(results.get("lab_results", {})),
            "recent_visits": _format_recent_visits(results.get("recent_appointments", {})),
            "recent_documents": _format_documents(results.get("documents", {})),
            # === CLINICAL ALERTS ===
            "alerts": _generate_alerts(
                patient,
                results.get("allergies", {}),
                results.get("medications", {}),
                results.get("lab_results", {}),
            ),
        }

        # Add current appointment if provided
        if appointment_id:
            apt = await client.get_appointment(appointment_id)
            context["current_visit"] = {
                "appointment_id": appointment_id,
                "scheduled_time": apt.get("scheduled_time"),
                "reason": apt.get("reason"),
                "status": apt.get("status"),
                "doctor_id": apt.get("doctor"),
                "office": apt.get("office"),
            }

            # Get clinical note if exists
            notes = await client.get_clinical_note(appointment_id)
            if notes.get("results"):
                note = notes["results"][0]
                context["current_visit"]["clinical_note"] = {
                    "chief_complaint": note.get("chief_complaint"),
                    "hpi": note.get("history_of_present_illness"),
                    "locked": note.get("locked", False),
                }

        # Add billing/insurance if requested
        if include_billing and "eligibility" in results:
            elig = results["eligibility"]
            context["insurance"] = {
                "primary": patient.get("primary_insurance"),
                "eligibility_status": (
                    elig.get("results", [{}])[0].get("status")
                    if elig.get("results") else "Unknown"
                ),
                "copay": (
                    elig.get("results", [{}])[0].get("copay")
                    if elig.get("results") else None
                ),
            }

        # Add memories from SimpleMem if configured
        if memory_client and memory_client.is_configured:
            try:
                patient_name = context["demographics"]["name"]
                memories = await memory_client.get_patient_memories(
                    patient_id, patient_name, limit=10
                )
                context["past_encounter_memories"] = memories.get("content", [])
            except Exception as e:
                context["past_encounter_memories"] = {"error": str(e)}

        return context

    @server.tool()
    async def drchrono_store_encounter_memory(
        patient_id: int,
        encounter_summary: str,
        chief_complaint: str | None = None,
        diagnosis: str | None = None,
        plan: str | None = None,
        appointment_id: int | None = None,
    ) -> dict:
        """Store a clinical encounter summary in persistent memory.

        Use this at the END of a patient visit to save key clinical information
        for future reference. This helps maintain continuity of care across visits.

        Stored memories can be retrieved with drchrono_get_clinical_context.

        Args:
            patient_id: Patient ID (required)
            encounter_summary: Brief summary of the encounter (required)
            chief_complaint: Chief complaint for this visit
            diagnosis: Diagnosis or assessment (comma-separated if multiple)
            plan: Treatment plan
            appointment_id: Link to specific appointment

        Returns:
            Confirmation of memory storage
        """
        if not memory_client or not memory_client.is_configured:
            return {
                "error": "Memory system not configured",
                "message": (
                    "SimpleMem is not configured. Set SIMPLEMEM_API_URL and "
                    "SIMPLEMEM_ACCESS_TOKEN environment variables."
                ),
            }

        # Get patient name
        patient = await client.get_patient(patient_id)
        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"

        # Get doctor info if appointment provided
        doctor_name = None
        visit_date = datetime.now().strftime("%Y-%m-%d")
        if appointment_id:
            apt = await client.get_appointment(appointment_id)
            visit_date = apt.get("scheduled_time", "")[:10]
            # Could fetch doctor name from doctors endpoint if needed

        # Parse diagnosis list if provided
        diagnosis_list = None
        if diagnosis:
            diagnosis_list = [d.strip() for d in diagnosis.split(",")]

        try:
            result = await memory_client.store_patient_encounter(
                patient_id=patient_id,
                patient_name=patient_name,
                encounter_summary=encounter_summary,
                visit_date=visit_date,
                doctor_name=doctor_name,
                chief_complaint=chief_complaint,
                diagnosis=diagnosis_list,
                plan=plan,
            )
            return {
                "success": True,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "visit_date": visit_date,
                "message": "Encounter memory stored successfully",
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store encounter memory",
            }

    @server.tool()
    async def drchrono_store_clinical_alert(
        patient_id: int,
        alert_type: str,
        alert_content: str,
        severity: str = "warning",
    ) -> dict:
        """Store a clinical alert/flag for a patient.

        Use this to flag important clinical information that should be
        surfaced on future visits, such as:
        - Drug allergies discovered during visit
        - Drug interactions to watch for
        - Critical lab values
        - Patient preferences or special considerations
        - Social/behavioral notes relevant to care

        Args:
            patient_id: Patient ID (required)
            alert_type: Type of alert - "allergy", "drug_interaction", "lab_critical",
                "patient_preference", "behavioral", "follow_up", "other"
            alert_content: Detailed description of the alert (required)
            severity: "info", "warning", or "critical" (default: warning)

        Returns:
            Confirmation of alert storage
        """
        if not memory_client or not memory_client.is_configured:
            return {
                "error": "Memory system not configured",
                "message": "SimpleMem is not configured.",
            }

        # Validate severity
        if severity not in ("info", "warning", "critical"):
            severity = "warning"

        # Get patient name
        patient = await client.get_patient(patient_id)
        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"

        try:
            result = await memory_client.store_clinical_alert(
                patient_id=patient_id,
                patient_name=patient_name,
                alert_type=alert_type,
                alert_content=alert_content,
                severity=severity,
            )
            return {
                "success": True,
                "patient_id": patient_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": f"Clinical alert stored for {patient_name}",
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store clinical alert",
            }

    @server.tool()
    async def drchrono_search_patient_history(
        patient_id: int,
        query: str,
        limit: int = 10,
    ) -> dict:
        """Search patient's clinical history in memory system.

        Use this to find specific information from past encounters, such as:
        - "previous cardiac workup"
        - "diabetes management history"
        - "past surgical procedures"
        - "medication changes"

        Args:
            patient_id: Patient ID (required)
            query: Natural language search query (required)
            limit: Maximum results (default 10)

        Returns:
            Matching memories from patient's history
        """
        if not memory_client or not memory_client.is_configured:
            return {
                "error": "Memory system not configured",
                "message": "SimpleMem is not configured.",
            }

        # Get patient name for better search
        patient = await client.get_patient(patient_id)
        patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}"

        # Combine patient identifier with query
        full_query = f"patient_id:{patient_id} {patient_name} {query}"

        try:
            results = await memory_client.search_memories(full_query, limit)
            return {
                "patient_id": patient_id,
                "patient_name": patient_name,
                "query": query,
                "results": results.get("content", []),
                "total_found": len(results.get("content", [])),
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to search patient history",
            }

    @server.tool()
    async def drchrono_get_clinical_display(
        patient_id: int | None = None,
        appointment_id: int | None = None,
        include_charts: bool = True,
        include_billing: bool = False,
    ) -> dict:
        """Get a beautiful interactive HTML display of patient clinical data.

        This tool returns MCP-UI compatible HTML with:
        - Formatted clinical sections (allergies, medications, problems, labs)
        - Interactive Chart.js visualizations (lab trends, vitals, visit frequency)
        - Color-coded alerts and severity indicators
        - Professional clinical layout optimized for doctor review

        Use this when you want a visual presentation of patient data.

        Args:
            patient_id: Patient ID (provide this OR appointment_id)
            appointment_id: Current appointment ID (will auto-fetch patient)
            include_charts: Include Chart.js visualizations (default True)
            include_billing: Include insurance/billing info (default False)

        Returns:
            dict with 'html' key containing MCP-UI compatible HTML content
        """
        # First get the clinical context data
        context = await drchrono_get_clinical_context(
            patient_id=patient_id,
            appointment_id=appointment_id,
            include_billing=include_billing,
        )

        if "error" in context:
            return context

        # Build the display HTML
        display_builder = ClinicalDisplayBuilder()

        # Patient header
        demographics = context.get("demographics", {})
        patient_name = demographics.get("name", "Unknown Patient")
        patient_age = demographics.get("age", "")
        patient_gender = demographics.get("gender", "")

        html_parts = []

        # Header with patient info
        html_parts.append(f"""
        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
                    color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 1.75rem;">{patient_name}</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                {patient_age} y/o {patient_gender} · ID: {context.get('patient_id')}
            </p>
        </div>
        """)

        # Current visit info if present
        if context.get("current_visit"):
            visit = context["current_visit"]
            html_parts.append(f"""
            <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9;
                        padding: 1rem; margin-bottom: 1rem; border-radius: 0 8px 8px 0;">
                <strong>Current Visit:</strong> {visit.get('reason', 'No reason specified')}
                <br><small style="color: #64748b;">
                    {visit.get('scheduled_time', '')} · Status: {visit.get('status', 'Unknown')}
                </small>
            </div>
            """)

        # Alerts section (critical first)
        alerts = context.get("alerts", [])
        if alerts:
            html_parts.append(display_builder.build_alerts_section(alerts))

        # Allergies (critical clinical info)
        allergies = context.get("allergies", [])
        html_parts.append(display_builder.build_allergies_section(allergies))

        # Active Medications
        medications = context.get("active_medications", [])
        html_parts.append(display_builder.build_medications_section(medications))

        # Active Problems
        problems = context.get("active_problems", [])
        html_parts.append(display_builder.build_problems_section(problems))

        # Recent Labs with optional chart
        labs = context.get("recent_labs", [])
        html_parts.append(display_builder.build_labs_section(labs))

        # Add charts if requested
        if include_charts and labs:
            # Group labs by test name for trend charts
            lab_groups: dict[str, list] = {}
            for lab in labs:
                test_name = lab.get("test", "Unknown")
                if test_name not in lab_groups:
                    lab_groups[test_name] = []
                lab_groups[test_name].append({
                    "date": lab.get("date", ""),
                    "value": lab.get("value", 0),
                    "unit": lab.get("unit", ""),
                })

            # Create charts for tests with multiple values
            chart_html = []
            for test_name, values in lab_groups.items():
                if len(values) >= 2:
                    # Parse normal range if available
                    normal_range = None
                    if labs:
                        for lab in labs:
                            if lab.get("test") == test_name and lab.get("normal_range"):
                                try:
                                    range_str = lab["normal_range"]
                                    if "-" in range_str:
                                        low, high = range_str.split("-")
                                        normal_range = (float(low.strip()), float(high.strip()))
                                except (ValueError, AttributeError):
                                    pass
                                break

                    chart = ClinicalChartBuilder.build_lab_trend_chart(
                        test_name, values, normal_range
                    )
                    chart_html.append(f"""
                    <div style="margin-bottom: 1rem;">
                        {chart}
                    </div>
                    """)

            if chart_html:
                html_parts.append(f"""
                <div style="background: #fff; border: 1px solid #e2e8f0;
                            border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #1e293b;">
                        📈 Lab Trends
                    </h3>
                    {''.join(chart_html[:3])}
                </div>
                """)

        # Recent Visits with chart
        visits = context.get("recent_visits", [])
        html_parts.append(display_builder.build_visits_section(visits))

        if include_charts and visits:
            visit_chart = ClinicalChartBuilder.build_visit_frequency_chart(visits)
            html_parts.append(f"""
            <div style="background: #fff; border: 1px solid #e2e8f0;
                        border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <h3 style="margin: 0 0 1rem 0; color: #1e293b;">
                    📅 Visit History
                </h3>
                {visit_chart}
            </div>
            """)

        # Problem distribution chart
        if include_charts and problems:
            problem_chart = ClinicalChartBuilder.build_problem_distribution_chart(
                [{"name": p.get("name", "")} for p in problems]
            )
            if problem_chart:
                html_parts.append(f"""
                <div style="background: #fff; border: 1px solid #e2e8f0;
                            border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #1e293b;">
                        🩺 Problem Categories
                    </h3>
                    {problem_chart}
                </div>
                """)

        # Medication timeline
        if include_charts and medications:
            med_data = [
                {
                    "name": m.get("name", ""),
                    "start_date": m.get("start_date", ""),
                }
                for m in medications
            ]
            med_chart = ClinicalChartBuilder.build_medication_timeline(med_data)
            html_parts.append(f"""
            <div style="background: #fff; border: 1px solid #e2e8f0;
                        border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <h3 style="margin: 0 0 1rem 0; color: #1e293b;">
                    💊 Medication Timeline
                </h3>
                {med_chart}
            </div>
            """)

        # Immunizations
        immunizations = context.get("immunizations", [])
        if immunizations:
            html_parts.append(display_builder.build_immunizations_section(immunizations))

        # Demographics and contact info
        contact = context.get("contact", {})
        html_parts.append(display_builder.build_demographics_section(demographics, contact))

        # Insurance if included
        if include_billing and context.get("insurance"):
            html_parts.append(display_builder.build_insurance_section(context["insurance"]))

        # Past encounter memories
        memories = context.get("past_encounter_memories", [])
        if memories and not isinstance(memories, dict):
            html_parts.append(display_builder.build_memories_section(memories))

        # Combine all parts into final HTML
        final_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px; margin: 0 auto; padding: 1rem;">
            {''.join(html_parts)}
            <footer style="text-align: center; color: #94a3b8; font-size: 0.75rem;
                          margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
                Retrieved: {context.get('retrieved_at', '')} · DrChrono MCP
            </footer>
        </div>
        """

        return {
            "html": final_html,
            "patient_id": context.get("patient_id"),
            "patient_name": patient_name,
            "content_type": "text/html",
            "mcp_ui": True,
        }


# ===================
# Helper functions
# ===================


def _calculate_age(dob: str | None) -> int | None:
    """Calculate age from date of birth."""
    if not dob:
        return None
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    except ValueError:
        return None


def _format_address(patient: dict) -> str | None:
    """Format patient address."""
    parts = []
    if patient.get("address"):
        parts.append(patient["address"])
    city_state = []
    if patient.get("city"):
        city_state.append(patient["city"])
    if patient.get("state"):
        city_state.append(patient["state"])
    if city_state:
        parts.append(", ".join(city_state))
    if patient.get("zip_code"):
        parts.append(patient["zip_code"])
    return " ".join(parts) if parts else None


def _format_allergies(allergies_response: dict) -> list[dict]:
    """Format allergies with severity for clinical display."""
    results = allergies_response.get("results", [])
    formatted = []
    for a in results:
        if a.get("status") == "active":
            formatted.append({
                "allergen": a.get("name"),
                "reaction": a.get("reaction"),
                "severity": a.get("severity", "unknown"),
                "onset_date": a.get("onset_date"),
            })
    return formatted


def _format_medications(meds_response: dict) -> list[dict]:
    """Format active medications for clinical display."""
    results = meds_response.get("results", [])
    formatted = []
    for m in results:
        if m.get("status") in ("active", None):
            formatted.append({
                "name": m.get("name"),
                "dose": m.get("dose"),
                "frequency": m.get("frequency"),
                "route": m.get("route"),
                "prescriber": m.get("prescriber"),
                "start_date": m.get("date_prescribed"),
                "refills_remaining": m.get("refills"),
            })
    return formatted


def _format_problems(problems_response: dict) -> list[dict]:
    """Format active problems/conditions."""
    results = problems_response.get("results", [])
    formatted = []
    for p in results:
        if p.get("status") in ("active", None):
            formatted.append({
                "name": p.get("name"),
                "icd_code": p.get("icd_code"),
                "onset_date": p.get("date_diagnosis"),
                "notes": p.get("notes"),
            })
    return formatted


def _format_vaccines(vaccines_response: dict) -> list[dict]:
    """Format immunization history."""
    results = vaccines_response.get("results", [])
    return [
        {
            "vaccine": v.get("name"),
            "date_administered": v.get("administered_date"),
            "cvx_code": v.get("cvx_code"),
        }
        for v in results[:15]  # Limit to recent
    ]


def _format_labs(labs_response: dict) -> list[dict]:
    """Format recent lab results with abnormal flags."""
    results = labs_response.get("results", [])
    return [
        {
            "test": r.get("test_name"),
            "value": r.get("value"),
            "unit": r.get("unit"),
            "normal_range": r.get("normal_range"),
            "abnormal": r.get("abnormal_flag"),
            "date": r.get("observation_date"),
        }
        for r in results
    ]


def _format_recent_visits(appointments_response: dict) -> list[dict]:
    """Format recent appointment history."""
    results = appointments_response.get("results", [])
    return [
        {
            "date": apt.get("scheduled_time"),
            "reason": apt.get("reason"),
            "status": apt.get("status"),
            "doctor_id": apt.get("doctor"),
        }
        for apt in results
        if apt.get("status") in ("Complete", "Checked In", "Arrived")
    ][:5]


def _format_documents(docs_response: dict) -> list[dict]:
    """Format recent documents."""
    results = docs_response.get("results", [])
    return [
        {
            "description": d.get("description"),
            "category": d.get("category"),
            "date": d.get("date"),
        }
        for d in results[:5]
    ]


def _generate_alerts(
    patient: dict,
    allergies: dict,
    medications: dict,
    labs: dict,
) -> list[dict]:
    """Generate clinical alerts based on patient data.

    Identifies:
    - Drug allergies present
    - Missing/outdated information
    - Abnormal lab values
    - Potential drug interactions (basic)
    """
    alerts = []

    # Alert for allergies
    allergy_list = allergies.get("results", [])
    active_allergies = [a for a in allergy_list if a.get("status") == "active"]
    if active_allergies:
        alerts.append({
            "type": "allergy_warning",
            "severity": "high",
            "message": f"Patient has {len(active_allergies)} documented allergies",
            "details": [a.get("name") for a in active_allergies],
        })

    # Alert for abnormal labs
    lab_results = labs.get("results", [])
    abnormal_labs = [r for r in lab_results if r.get("abnormal_flag")]
    if abnormal_labs:
        alerts.append({
            "type": "abnormal_labs",
            "severity": "medium",
            "message": f"{len(abnormal_labs)} abnormal lab results in last 90 days",
            "details": [
                f"{r.get('test_name')}: {r.get('value')} ({r.get('abnormal_flag')})"
                for r in abnormal_labs[:5]
            ],
        })

    # Alert for missing emergency contact
    if not patient.get("emergency_contact_name"):
        alerts.append({
            "type": "missing_info",
            "severity": "low",
            "message": "No emergency contact on file",
        })

    # Alert for multiple medications (polypharmacy risk)
    med_list = medications.get("results", [])
    active_meds = [m for m in med_list if m.get("status") in ("active", None)]
    if len(active_meds) >= 10:
        alerts.append({
            "type": "polypharmacy",
            "severity": "medium",
            "message": f"Patient on {len(active_meds)} medications - review for interactions",
        })

    return alerts
