"""Clinical UI display builder for MCP-UI rendering.

Generates beautiful, interactive HTML displays for clinical data that
MCP-UI clients can render for doctors and clinical staff.
"""

from datetime import datetime
from typing import Any


class ClinicalDisplayBuilder:
    """Builds HTML clinical displays optimized for MCP-UI rendering.

    Provides consistent, accessible clinical displays with:
    - Color-coded severity indicators
    - Collapsible sections
    - Interactive tables
    - Alert banners
    - Responsive design for mobile/tablet
    """

    # Clinical color scheme
    COLORS = {
        "critical": "#dc2626",  # Red
        "warning": "#f59e0b",  # Amber
        "info": "#3b82f6",  # Blue
        "success": "#10b981",  # Green
        "muted": "#6b7280",  # Gray
        "primary": "#2563eb",  # Primary blue
        "background": "#f8fafc",
        "card": "#ffffff",
        "border": "#e2e8f0",
        "text": "#1e293b",
        "text_muted": "#64748b",
    }

    @classmethod
    def build_clinical_context_display(cls, context: dict[str, Any]) -> str:
        """Build complete clinical context display.

        Args:
            context: Clinical context data from drchrono_get_clinical_context

        Returns:
            HTML string for MCP-UI rendering
        """
        demographics = context.get("demographics", {})
        patient_name = demographics.get("name", "Unknown Patient")
        age = demographics.get("age")
        gender = demographics.get("gender", "")

        html_parts = [
            cls._build_styles(),
            cls._build_header(patient_name, age, gender, context.get("patient_id")),
            cls._build_alerts_section(context.get("alerts", [])),
            cls._build_current_visit(context.get("current_visit")),
            cls._build_allergies_section(context.get("allergies", [])),
            cls._build_medications_section(context.get("active_medications", [])),
            cls._build_problems_section(context.get("active_problems", [])),
            cls._build_labs_section(context.get("recent_labs", [])),
            cls._build_visits_section(context.get("recent_visits", [])),
            cls._build_demographics_section(demographics, context.get("contact", {})),
        ]

        if context.get("insurance"):
            html_parts.append(cls._build_insurance_section(context["insurance"]))

        if context.get("past_encounter_memories"):
            html_parts.append(cls._build_memories_section(context["past_encounter_memories"]))

        return f"""
        <div class="clinical-context">
            {"".join(html_parts)}
            <footer class="footer">
                Retrieved: {context.get("retrieved_at", datetime.now().isoformat())}
            </footer>
        </div>
        """

    @classmethod
    def _build_styles(cls) -> str:
        """Build CSS styles for clinical display."""
        return f"""
        <style>
            .clinical-context {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: {cls.COLORS["background"]};
                color: {cls.COLORS["text"]};
                padding: 1rem;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background: linear-gradient(135deg, {cls.COLORS["primary"]} 0%, #1d4ed8 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
            }}
            .header h1 {{
                margin: 0 0 0.5rem 0;
                font-size: 1.75rem;
            }}
            .header .patient-meta {{
                opacity: 0.9;
                font-size: 1rem;
            }}
            .card {{
                background: {cls.COLORS["card"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .card-header {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.75rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid {cls.COLORS["border"]};
            }}
            .card-title {{
                font-weight: 600;
                font-size: 1.1rem;
                margin: 0;
            }}
            .badge {{
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 500;
            }}
            .badge-critical {{
                background: #fef2f2;
                color: {cls.COLORS["critical"]};
                border: 1px solid #fecaca;
            }}
            .badge-warning {{
                background: #fffbeb;
                color: {cls.COLORS["warning"]};
                border: 1px solid #fde68a;
            }}
            .badge-info {{
                background: #eff6ff;
                color: {cls.COLORS["info"]};
                border: 1px solid #bfdbfe;
            }}
            .alert {{
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
            }}
            .alert-critical {{
                background: #fef2f2;
                border-left: 4px solid {cls.COLORS["critical"]};
            }}
            .alert-warning {{
                background: #fffbeb;
                border-left: 4px solid {cls.COLORS["warning"]};
            }}
            .alert-info {{
                background: #eff6ff;
                border-left: 4px solid {cls.COLORS["info"]};
            }}
            .alert-icon {{
                font-size: 1.25rem;
            }}
            .alert-content {{
                flex: 1;
            }}
            .alert-title {{
                font-weight: 600;
                margin: 0 0 0.25rem 0;
            }}
            .alert-details {{
                font-size: 0.875rem;
                color: {cls.COLORS["text_muted"]};
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }}
            th, td {{
                text-align: left;
                padding: 0.5rem;
                border-bottom: 1px solid {cls.COLORS["border"]};
            }}
            th {{
                font-weight: 600;
                color: {cls.COLORS["text_muted"]};
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
            .abnormal {{
                color: {cls.COLORS["critical"]};
                font-weight: 600;
            }}
            .empty-state {{
                text-align: center;
                padding: 1rem;
                color: {cls.COLORS["text_muted"]};
                font-style: italic;
            }}
            .two-column {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid {cls.COLORS["border"]};
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .detail-label {{
                color: {cls.COLORS["text_muted"]};
                font-size: 0.875rem;
            }}
            .detail-value {{
                font-weight: 500;
            }}
            .footer {{
                text-align: center;
                padding: 1rem;
                color: {cls.COLORS["text_muted"]};
                font-size: 0.75rem;
            }}
            .section-icon {{
                font-size: 1.25rem;
            }}
            .current-visit {{
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 1px solid #a7f3d0;
            }}
        </style>
        """

    @classmethod
    def _build_header(cls, name: str, age: int | None, gender: str, patient_id: int | None) -> str:
        """Build patient header."""
        age_str = f"{age}yo" if age else ""
        gender_short = gender[0].upper() if gender else ""
        meta_parts = [p for p in [age_str, gender_short] if p]
        meta = " | ".join(meta_parts) if meta_parts else ""

        return f"""
        <div class="header">
            <h1>{cls._escape(name)}</h1>
            <div class="patient-meta">
                {meta}
                {f" | ID: {patient_id}" if patient_id else ""}
            </div>
        </div>
        """

    @classmethod
    def _build_alerts_section(cls, alerts: list[dict]) -> str:
        """Build clinical alerts section."""
        if not alerts:
            return ""

        alerts_html = []
        for alert in alerts:
            severity = alert.get("severity", "info")
            if severity == "high":
                severity = "critical"
            elif severity == "medium":
                severity = "warning"
            else:
                severity = "info"

            icon = "⚠️" if severity == "critical" else "⚡" if severity == "warning" else "ℹ️"

            details = alert.get("details", [])
            details_html = ""
            if details:
                details_html = "<br>• " + "<br>• ".join(cls._escape(str(d)) for d in details[:5])

            alerts_html.append(f"""
                <div class="alert alert-{severity}">
                    <span class="alert-icon">{icon}</span>
                    <div class="alert-content">
                        <p class="alert-title">{cls._escape(alert.get("message", ""))}</p>
                        {f'<p class="alert-details">{details_html}</p>' if details_html else ""}
                    </div>
                </div>
            """)

        return f"""
        <div class="alerts-section">
            {"".join(alerts_html)}
        </div>
        """

    @classmethod
    def _build_current_visit(cls, visit: dict | None) -> str:
        """Build current visit card."""
        if not visit:
            return ""

        return f"""
        <div class="card current-visit">
            <div class="card-header">
                <span class="section-icon">📋</span>
                <h2 class="card-title">Current Visit</h2>
            </div>
            <div class="two-column">
                <div>
                    <div class="detail-row">
                        <span class="detail-label">Time</span>
                        <span class="detail-value">
                            {cls._escape(visit.get("scheduled_time", ""))}
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Reason</span>
                        <span class="detail-value">
                            {cls._escape(visit.get("reason", "Not specified"))}
                        </span>
                    </div>
                </div>
                <div>
                    <div class="detail-row">
                        <span class="detail-label">Status</span>
                        <span class="detail-value">{cls._escape(visit.get("status", ""))}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Appointment ID</span>
                        <span class="detail-value">{visit.get("appointment_id", "")}</span>
                    </div>
                </div>
            </div>
            {cls._build_clinical_note_preview(visit.get("clinical_note"))}
        </div>
        """

    @classmethod
    def _build_clinical_note_preview(cls, note: dict | None) -> str:
        """Build clinical note preview."""
        if not note:
            return ""

        complaint = cls._escape(note.get("chief_complaint", "Not documented"))
        return f"""
        <div style="margin-top: 1rem; padding-top: 1rem;
                    border-top: 1px solid #a7f3d0;">
            <strong>Chief Complaint:</strong> {complaint}
        </div>
        """

    @classmethod
    def _build_allergies_section(cls, allergies: list[dict]) -> str:
        """Build allergies card - CRITICAL section."""
        if not allergies:
            content = '<p class="empty-state">No known allergies documented</p>'
        else:
            rows = []
            for a in allergies:
                severity_class = "abnormal" if a.get("severity") == "severe" else ""
                rows.append(f"""
                    <tr>
                        <td class="{severity_class}">{cls._escape(a.get("allergen", ""))}</td>
                        <td>{cls._escape(a.get("reaction", "Not specified"))}</td>
                        <td>{cls._escape(a.get("severity", "Unknown"))}</td>
                    </tr>
                """)
            content = f"""
                <table>
                    <thead>
                        <tr>
                            <th>Allergen</th>
                            <th>Reaction</th>
                            <th>Severity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            """

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">🚨</span>
                <h2 class="card-title">Allergies</h2>
                <span class="badge badge-critical">{len(allergies)} documented</span>
            </div>
            {content}
        </div>
        """

    @classmethod
    def _build_medications_section(cls, medications: list[dict]) -> str:
        """Build active medications card."""
        if not medications:
            content = '<p class="empty-state">No active medications</p>'
        else:
            rows = []
            for m in medications:
                rows.append(f"""
                    <tr>
                        <td><strong>{cls._escape(m.get("name", ""))}</strong></td>
                        <td>{cls._escape(m.get("dose", ""))}</td>
                        <td>{cls._escape(m.get("frequency", ""))}</td>
                    </tr>
                """)
            content = f"""
                <table>
                    <thead>
                        <tr>
                            <th>Medication</th>
                            <th>Dose</th>
                            <th>Frequency</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            """

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">💊</span>
                <h2 class="card-title">Active Medications</h2>
                <span class="badge badge-info">{len(medications)} active</span>
            </div>
            {content}
        </div>
        """

    @classmethod
    def _build_problems_section(cls, problems: list[dict]) -> str:
        """Build active problems card."""
        if not problems:
            content = '<p class="empty-state">No active problems documented</p>'
        else:
            rows = []
            for p in problems:
                rows.append(f"""
                    <tr>
                        <td>{cls._escape(p.get("name", ""))}</td>
                        <td><code>{cls._escape(p.get("icd_code", "") or "N/A")}</code></td>
                        <td>{cls._escape(p.get("onset_date", "") or "Unknown")}</td>
                    </tr>
                """)
            content = f"""
                <table>
                    <thead>
                        <tr>
                            <th>Condition</th>
                            <th>ICD Code</th>
                            <th>Onset</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            """

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">📋</span>
                <h2 class="card-title">Active Problems</h2>
                <span class="badge badge-warning">{len(problems)} active</span>
            </div>
            {content}
        </div>
        """

    @classmethod
    def _build_labs_section(cls, labs: list[dict]) -> str:
        """Build recent labs card with abnormal highlighting."""
        if not labs:
            content = '<p class="empty-state">No recent lab results (last 90 days)</p>'
        else:
            rows = []
            for lab in labs:
                is_abnormal = lab.get("abnormal")
                abnormal_class = "abnormal" if is_abnormal else ""
                value_display = f"{lab.get('value', '')} {lab.get('unit', '')}".strip()
                if is_abnormal:
                    value_display = f"⚠️ {value_display}"

                rows.append(f"""
                    <tr>
                        <td>{cls._escape(lab.get("test", ""))}</td>
                        <td class="{abnormal_class}">{cls._escape(value_display)}</td>
                        <td>{cls._escape(lab.get("normal_range", "") or "N/A")}</td>
                        <td>{cls._escape(lab.get("date", "") or "")}</td>
                    </tr>
                """)
            content = f"""
                <table>
                    <thead>
                        <tr>
                            <th>Test</th>
                            <th>Value</th>
                            <th>Normal Range</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(rows)}
                    </tbody>
                </table>
            """

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">🔬</span>
                <h2 class="card-title">Recent Lab Results</h2>
            </div>
            {content}
        </div>
        """

    @classmethod
    def _build_visits_section(cls, visits: list[dict]) -> str:
        """Build recent visits card."""
        if not visits:
            return ""

        rows = []
        for v in visits:
            rows.append(f"""
                <tr>
                    <td>{cls._escape(v.get("date", "")[:10] if v.get("date") else "")}</td>
                    <td>{cls._escape(v.get("reason", "Not specified"))}</td>
                    <td>{cls._escape(v.get("status", ""))}</td>
                </tr>
            """)

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">📅</span>
                <h2 class="card-title">Recent Visits</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Reason</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        """

    @classmethod
    def _build_demographics_section(cls, demographics: dict, contact: dict) -> str:
        """Build demographics and contact info card."""
        dob = cls._escape(demographics.get("date_of_birth", ""))
        gender = cls._escape(demographics.get("gender", ""))
        lang = cls._escape(demographics.get("preferred_language", "") or "English")
        phone = cls._escape(
            contact.get("cell_phone", "") or contact.get("home_phone", "") or "Not on file"
        )
        email = cls._escape(contact.get("email", "") or "Not on file")
        emergency = cls._escape(contact.get("emergency_contact", "") or "Not on file")

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">👤</span>
                <h2 class="card-title">Demographics & Contact</h2>
            </div>
            <div class="two-column">
                <div>
                    <div class="detail-row">
                        <span class="detail-label">Date of Birth</span>
                        <span class="detail-value">{dob}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Gender</span>
                        <span class="detail-value">{gender}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Language</span>
                        <span class="detail-value">{lang}</span>
                    </div>
                </div>
                <div>
                    <div class="detail-row">
                        <span class="detail-label">Phone</span>
                        <span class="detail-value">{phone}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Email</span>
                        <span class="detail-value">{email}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Emergency Contact</span>
                        <span class="detail-value">{emergency}</span>
                    </div>
                </div>
            </div>
        </div>
        """

    @classmethod
    def _build_insurance_section(cls, insurance: dict) -> str:
        """Build insurance info card."""
        primary = cls._escape(str(insurance.get("primary", "Not on file")))
        eligibility = cls._escape(insurance.get("eligibility_status", "Unknown"))

        copay_html = ""
        if insurance.get("copay"):
            copay_html = f"""
            <div class="detail-row">
                <span class="detail-label">Copay</span>
                <span class="detail-value">${insurance.get("copay", "N/A")}</span>
            </div>
            """

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">🏥</span>
                <h2 class="card-title">Insurance</h2>
            </div>
            <div class="detail-row">
                <span class="detail-label">Primary Insurance</span>
                <span class="detail-value">{primary}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Eligibility Status</span>
                <span class="detail-value">{eligibility}</span>
            </div>
            {copay_html}
        </div>
        """

    @classmethod
    def _build_memories_section(cls, memories: list | dict) -> str:
        """Build past encounter memories section."""
        if isinstance(memories, dict) and "error" in memories:
            return ""

        if not memories:
            return ""

        memory_items = []
        for mem in memories if isinstance(memories, list) else []:
            if isinstance(mem, str):
                memory_items.append(f"<li>{cls._escape(mem[:200])}</li>")
            elif isinstance(mem, dict):
                content = mem.get("content", str(mem))
                memory_items.append(f"<li>{cls._escape(str(content)[:200])}</li>")

        if not memory_items:
            return ""

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">🧠</span>
                <h2 class="card-title">Clinical Memory (Past Encounters)</h2>
            </div>
            <ul style="margin: 0; padding-left: 1.5rem;">
                {"".join(memory_items[:5])}
            </ul>
        </div>
        """

    @staticmethod
    def _escape(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    # ===================
    # Public API methods
    # ===================

    def build_alerts_section(self, alerts: list[dict]) -> str:
        """Build clinical alerts section."""
        return self._build_alerts_section(alerts)

    def build_allergies_section(self, allergies: list[dict]) -> str:
        """Build allergies card - CRITICAL section."""
        return self._build_allergies_section(allergies)

    def build_medications_section(self, medications: list[dict]) -> str:
        """Build active medications card."""
        return self._build_medications_section(medications)

    def build_problems_section(self, problems: list[dict]) -> str:
        """Build active problems card."""
        return self._build_problems_section(problems)

    def build_labs_section(self, labs: list[dict]) -> str:
        """Build recent labs card with abnormal highlighting."""
        return self._build_labs_section(labs)

    def build_visits_section(self, visits: list[dict]) -> str:
        """Build recent visits card."""
        return self._build_visits_section(visits)

    def build_demographics_section(self, demographics: dict, contact: dict) -> str:
        """Build demographics and contact info card."""
        return self._build_demographics_section(demographics, contact)

    def build_insurance_section(self, insurance: dict) -> str:
        """Build insurance info card."""
        return self._build_insurance_section(insurance)

    def build_memories_section(self, memories: list | dict) -> str:
        """Build past encounter memories section."""
        return self._build_memories_section(memories)

    def build_immunizations_section(self, immunizations: list[dict]) -> str:
        """Build immunizations/vaccines card."""
        if not immunizations:
            return ""

        rows = []
        for v in immunizations:
            rows.append(f"""
                <tr>
                    <td>{self._escape(v.get("vaccine", ""))}</td>
                    <td>{self._escape(v.get("date_administered", "") or "Unknown")}</td>
                    <td><code>{self._escape(v.get("cvx_code", "") or "N/A")}</code></td>
                </tr>
            """)

        return f"""
        <div class="card">
            <div class="card-header">
                <span class="section-icon">💉</span>
                <h2 class="card-title">Immunizations</h2>
                <span class="badge badge-info">{len(immunizations)} recorded</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Vaccine</th>
                        <th>Date</th>
                        <th>CVX Code</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        """
