"""Appointment card component for schedule display.

Displays appointment information with:
- Time and duration
- Patient name and reason
- Status indicators
- Quick actions
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.theme import get_icon

AppointmentStatus = Literal[
    "scheduled", "checked_in", "in_room", "complete", "cancelled", "no_show"
]


class AppointmentCard(BaseComponent):
    """A card component for displaying appointment information.

    Features:
    - Time prominence with visual schedule indicator
    - Status badges with semantic coloring
    - Patient quick reference
    - Optional action buttons
    """

    def __init__(
        self,
        scheduled_time: str,
        patient_name: str,
        reason: str | None = None,
        duration: int = 30,
        status: AppointmentStatus = "scheduled",
        appointment_id: int | str | None = None,
        office: str | None = None,
        provider: str | None = None,
        notes: str | None = None,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize appointment card.

        Args:
            scheduled_time: Appointment time (ISO format or display string)
            patient_name: Patient full name
            reason: Visit reason/chief complaint
            duration: Duration in minutes
            status: Current appointment status
            appointment_id: Appointment ID for actions
            office: Office/location name
            provider: Provider name
            notes: Additional notes
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._scheduled_time = scheduled_time
        self._patient_name = patient_name
        self._reason = reason
        self._duration = duration
        self._status = status
        self._appointment_id = appointment_id
        self._office = office
        self._provider = provider
        self._notes = notes
        self._actions: list[tuple[str, str, str | None]] = []

        self.add_class("appointment-card", f"appointment-card--{status}")

    @property
    def display_time(self) -> str:
        """Get formatted display time."""
        try:
            # Try to parse ISO format
            dt = datetime.fromisoformat(self._scheduled_time.replace("Z", "+00:00"))
            return dt.strftime("%I:%M %p").lstrip("0")
        except (ValueError, AttributeError):
            # Fall back to raw string
            return self._scheduled_time

    @property
    def display_date(self) -> str:
        """Get formatted display date."""
        try:
            dt = datetime.fromisoformat(self._scheduled_time.replace("Z", "+00:00"))
            return dt.strftime("%b %d, %Y")
        except (ValueError, AttributeError):
            return ""

    def add_action(self, text: str, url: str, icon: str | None = None) -> AppointmentCard:
        """Add an action button.

        Args:
            text: Button text
            url: Button URL
            icon: Optional icon name

        Returns:
            Self for chaining
        """
        self._actions.append((text, url, icon))
        return self

    def _get_status_config(self) -> tuple[str, str, str]:
        """Get status display configuration (label, color class, icon)."""
        config = {
            "scheduled": ("Scheduled", "status--info", "calendar"),
            "checked_in": ("Checked In", "status--success", "check"),
            "in_room": ("In Room", "status--warning", "user"),
            "complete": ("Complete", "status--success", "check"),
            "cancelled": ("Cancelled", "status--critical", "x"),
            "no_show": ("No Show", "status--critical", "alert"),
        }
        return config.get(self._status, ("Unknown", "status--info", "calendar"))

    def _build_status_badge(self) -> str:
        """Build status badge."""
        label, color_class, icon_name = self._get_status_config()
        return f"""
            <span class="appointment-card__status {color_class}">
                {get_icon(icon_name, size=14)}
                {self._escape(label)}
            </span>
        """

    def _build_actions(self) -> str:
        """Build action buttons."""
        if not self._actions:
            return ""

        buttons = []
        for text, url, icon in self._actions:
            icon_html = get_icon(icon, size=14) if icon else ""
            buttons.append(f'''
                <a href="{self._escape(url)}" class="appointment-card__action">
                    {icon_html}
                    {self._escape(text)}
                </a>
            ''')

        return f'<div class="appointment-card__actions">{"".join(buttons)}</div>'

    def build(self) -> str:
        """Build the appointment card HTML."""
        styles = self._get_component_styles()

        reason_html = ""
        if self._reason:
            reason_html = f"""
                <div class="appointment-card__reason">
                    <strong>Reason:</strong> {self._escape(self._reason)}
                </div>
            """

        location_parts = []
        if self._office:
            # Office can be an ID (int) or name (str)
            location_parts.append(str(self._office))
        if self._provider:
            location_parts.append(f"with {self._provider}")

        location_html = ""
        if location_parts:
            location_html = f"""
                <div class="appointment-card__location">
                    {get_icon("building", size=14)}
                    {self._escape(" ".join(location_parts))}
                </div>
            """

        notes_html = ""
        if self._notes:
            notes_html = f"""
                <div class="appointment-card__notes">{self._escape(self._notes)}</div>
            """

        return f"""
            <style>{styles}</style>
            <article {self.attr_string}>
                <div class="appointment-card__time-block">
                    <span class="appointment-card__time">{self._escape(self.display_time)}</span>
                    <span class="appointment-card__duration">{self._duration} min</span>
                </div>
                <div class="appointment-card__content">
                    <div class="appointment-card__header">
                        <span class="appointment-card__patient">
                            {self._escape(self._patient_name)}
                        </span>
                        {self._build_status_badge()}
                    </div>
                    {reason_html}
                    {location_html}
                    {notes_html}
                    {self._build_actions()}
                </div>
            </article>
        """

    @staticmethod
    def _get_component_styles() -> str:
        """Get component-specific CSS."""
        return """
            .appointment-card {
                display: flex;
                gap: var(--space-4);
                padding: var(--space-4);
                background: var(--bg-card);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-sm);
                transition: all var(--transition-fast);
            }

            .appointment-card:hover {
                box-shadow: var(--shadow-md), var(--glow-card);
                transform: translateY(-2px);
            }

            .appointment-card--cancelled,
            .appointment-card--no_show {
                opacity: 0.6;
                border-left: 4px solid var(--critical);
            }

            .appointment-card--checked_in {
                border-left: 4px solid var(--success);
            }

            .appointment-card--in_room {
                border-left: 4px solid var(--warning);
                box-shadow: var(--shadow-sm), var(--glow-warning);
            }

            .appointment-card__time-block {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: var(--space-3);
                background: var(--bg-elevated);
                border-radius: var(--radius-md);
                min-width: 80px;
                text-align: center;
            }

            .appointment-card__time {
                font-family: var(--font-mono);
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary);
                line-height: 1.2;
            }

            .appointment-card__duration {
                font-size: 0.75rem;
                color: var(--text-tertiary);
                margin-top: var(--space-1);
            }

            .appointment-card__content {
                flex: 1;
                min-width: 0;
            }

            .appointment-card__header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: var(--space-2);
                margin-bottom: var(--space-2);
            }

            .appointment-card__patient {
                font-family: var(--font-display);
                font-size: 1.125rem;
                font-weight: 500;
                color: var(--text-primary);
            }

            .appointment-card__status {
                display: inline-flex;
                align-items: center;
                gap: var(--space-1);
                padding: var(--space-1) var(--space-2);
                font-size: 0.75rem;
                font-weight: 500;
                border-radius: var(--radius-full);
            }

            .status--info {
                background: var(--info-bg);
                color: var(--info-text);
                border: 1px solid var(--info-border);
            }

            .status--success {
                background: var(--success-bg);
                color: var(--success-text);
                border: 1px solid var(--success-border);
            }

            .status--warning {
                background: var(--warning-bg);
                color: var(--warning-text);
                border: 1px solid var(--warning-border);
            }

            .status--critical {
                background: var(--critical-bg);
                color: var(--critical-text);
                border: 1px solid var(--critical-border);
            }

            .appointment-card__reason {
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-bottom: var(--space-2);
            }

            .appointment-card__location {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                font-size: 0.75rem;
                color: var(--text-tertiary);
            }

            .appointment-card__notes {
                font-size: 0.75rem;
                color: var(--text-tertiary);
                font-style: italic;
                margin-top: var(--space-2);
                padding-top: var(--space-2);
                border-top: 1px solid var(--border-secondary);
            }

            .appointment-card__actions {
                display: flex;
                gap: var(--space-2);
                margin-top: var(--space-3);
            }

            .appointment-card__action {
                display: inline-flex;
                align-items: center;
                gap: var(--space-1);
                padding: var(--space-1) var(--space-2);
                font-size: 0.75rem;
                font-weight: 500;
                color: var(--accent-primary);
                background: transparent;
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-sm);
                text-decoration: none;
                transition: all var(--transition-fast);
            }

            .appointment-card__action:hover {
                background: var(--accent-primary);
                color: var(--text-inverse);
                border-color: var(--accent-primary);
            }

            @media (max-width: 480px) {
                .appointment-card {
                    flex-direction: column;
                }

                .appointment-card__time-block {
                    flex-direction: row;
                    justify-content: flex-start;
                    gap: var(--space-3);
                }
            }
        """


class AppointmentList(BaseComponent):
    """A list of appointment cards."""

    def __init__(
        self,
        appointments: list[dict],
        show_date_headers: bool = True,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize appointment list.

        Args:
            appointments: List of appointment dicts
            show_date_headers: Group by date with headers
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._appointments = appointments
        self._show_date_headers = show_date_headers

        self.add_class("appointment-list")

    def build(self) -> str:
        """Build the appointment list HTML."""
        if not self._appointments:
            return f"""
                <div class="appointment-list__empty">
                    {get_icon("calendar", size=32)}
                    <p>No appointments scheduled</p>
                </div>
            """

        cards = []
        for apt in self._appointments:
            first = apt.get("patient_first_name", "")
            last = apt.get("patient_last_name", "")
            patient_name = f"{first} {last}".strip() or "Unknown"
            card = AppointmentCard(
                scheduled_time=apt.get("scheduled_time", ""),
                patient_name=patient_name,
                reason=apt.get("reason"),
                duration=apt.get("duration", 30),
                status=apt.get("status", "scheduled"),
                appointment_id=apt.get("id"),
                office=apt.get("office"),
                notes=apt.get("notes"),
            )
            cards.append(card.build())

        styles = """
            <style>
                .appointment-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--space-3);
                }

                .appointment-list__empty {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: var(--space-3);
                    padding: var(--space-8);
                    color: var(--text-secondary);
                    text-align: center;
                }

                .appointment-list__date-header {
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: var(--text-secondary);
                    padding: var(--space-2) 0;
                    border-bottom: 1px solid var(--border-secondary);
                    margin-bottom: var(--space-2);
                }
            </style>
        """

        return f"""
            {styles}
            <div {self.attr_string}>
                {"".join(cards)}
            </div>
        """


def create_appointment_card_from_data(appointment_data: dict) -> AppointmentCard:
    """Factory for creating AppointmentCard from API response.

    Args:
        appointment_data: Appointment dict from DrChrono API

    Returns:
        Configured AppointmentCard component
    """
    patient = appointment_data.get("patient", {})
    first = patient.get("first_name", "")
    last = patient.get("last_name", "")
    patient_name = f"{first} {last}".strip() or "Patient"

    return AppointmentCard(
        scheduled_time=appointment_data.get("scheduled_time", ""),
        patient_name=patient_name,
        reason=appointment_data.get("reason"),
        duration=appointment_data.get("duration", 30),
        status=appointment_data.get("status", "scheduled"),
        appointment_id=appointment_data.get("id"),
        office=appointment_data.get("office"),
    )
