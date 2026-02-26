"""Patient header component for identity display.

A clean, professional header for patient identification:
- Name, age, gender, DOB
- Patient ID and MRN
- No gradients, no decorative effects
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.theme import get_icon


def calculate_age(dob: str | date) -> int | None:
    """Calculate age from date of birth."""
    try:
        if isinstance(dob, str):
            birth_date = datetime.strptime(dob[:10], "%Y-%m-%d").date()
        else:
            birth_date = dob

        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    except (ValueError, TypeError):
        return None


class PatientHeader(BaseComponent):
    """Patient identity header with demographics."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: str | date | None = None,
        gender: str | None = None,
        patient_id: int | str | None = None,
        mrn: str | None = None,
        photo_url: str | None = None,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        super().__init__(css_class, **attrs)
        self._first_name = first_name
        self._last_name = last_name
        self._dob = date_of_birth
        self._gender = gender
        self._patient_id = patient_id
        self._mrn = mrn
        self._photo_url = photo_url
        self._actions: list[tuple[str, str, str | None]] = []

        self.add_class("patient-header")

    @property
    def full_name(self) -> str:
        return f"{self._first_name} {self._last_name}"

    @property
    def age(self) -> int | None:
        if self._dob:
            return calculate_age(self._dob)
        return None

    @property
    def gender_abbrev(self) -> str:
        if not self._gender:
            return ""
        return self._gender[0].upper()

    def add_action(self, text: str, url: str, icon: str | None = None) -> PatientHeader:
        self._actions.append((text, url, icon))
        return self

    def _build_avatar(self) -> str:
        if self._photo_url:
            return f'''
                <div class="patient-header__avatar">
                    <img src="{self._escape(self._photo_url)}" alt="" />
                </div>
            '''

        initials = f"{self._first_name[0]}{self._last_name[0]}".upper()
        return f"""
            <div class="patient-header__avatar patient-header__avatar--initials">
                {initials}
            </div>
        """

    def _build_demographics(self) -> str:
        parts = []
        if self.age is not None:
            parts.append(f"{self.age}yo")
        if self.gender_abbrev:
            parts.append(self.gender_abbrev)

        sep = " \u00b7 "
        demo_text = sep.join(parts) if parts else ""

        dob_display = ""
        if self._dob:
            dob_str = str(self._dob)[:10] if isinstance(self._dob, (str, date)) else ""
            dob_display = (
                f"<span class='patient-header__dob'>DOB: {self._escape(dob_str)}</span>"
            )

        return f"""
            <div class="patient-header__demographics">
                <span class="patient-header__age-gender">{demo_text}</span>
                {dob_display}
            </div>
        """

    def _build_identifiers(self) -> str:
        parts = []
        if self._patient_id:
            parts.append(f"ID: {self._escape(str(self._patient_id))}")
        if self._mrn:
            parts.append(f"MRN: {self._escape(self._mrn)}")
        if not parts:
            return ""
        sep = " \u00b7 "
        joined = sep.join(parts)
        return f"""
            <div class="patient-header__identifiers">
                {joined}
            </div>
        """

    def _build_actions(self) -> str:
        if not self._actions:
            return ""
        buttons = []
        for text, url, icon in self._actions:
            icon_html = get_icon(icon, size=14) if icon else ""
            buttons.append(f'''
                <a href="{self._escape(url)}" class="patient-header__action">
                    {icon_html}{self._escape(text)}
                </a>
            ''')
        return f'<div class="patient-header__actions">{"".join(buttons)}</div>'

    def build(self) -> str:
        styles = self._get_component_styles()
        return f"""
            <style>{styles}</style>
            <header {self.attr_string}>
                <div class="patient-header__content">
                    {self._build_avatar()}
                    <div class="patient-header__info">
                        <h1 class="patient-header__name">{self._escape(self.full_name)}</h1>
                        {self._build_demographics()}
                        {self._build_identifiers()}
                    </div>
                </div>
                {self._build_actions()}
            </header>
        """

    @staticmethod
    def _get_component_styles() -> str:
        return """
            .patient-header {
                background: var(--bg-elevated);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-lg);
                padding: var(--space-5) var(--space-6);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: var(--space-4);
                flex-wrap: wrap;
            }

            .patient-header__content {
                display: flex;
                align-items: center;
                gap: var(--space-4);
            }

            .patient-header__avatar {
                width: 48px;
                height: 48px;
                border-radius: var(--radius-full);
                overflow: hidden;
                flex-shrink: 0;
            }

            .patient-header__avatar img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .patient-header__avatar--initials {
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--accent-primary);
                color: var(--text-inverse);
                font-size: 1rem;
                font-weight: 600;
            }

            .patient-header__name {
                font-size: 1.25rem;
                font-weight: 600;
                margin: 0;
                line-height: 1.3;
            }

            .patient-header__demographics {
                display: flex;
                align-items: center;
                gap: var(--space-3);
                font-size: 0.8125rem;
                color: var(--text-secondary);
                margin-top: 2px;
            }

            .patient-header__age-gender {
                font-weight: 500;
            }

            .patient-header__dob {
                color: var(--text-tertiary);
            }

            .patient-header__identifiers {
                font-size: 0.6875rem;
                font-family: var(--font-mono);
                color: var(--text-tertiary);
                margin-top: 2px;
            }

            .patient-header__actions {
                display: flex;
                gap: var(--space-2);
            }

            .patient-header__action {
                display: inline-flex;
                align-items: center;
                gap: var(--space-1);
                padding: var(--space-2) var(--space-3);
                font-size: 0.8125rem;
                font-weight: 500;
                color: var(--text-secondary);
                background: var(--bg-primary);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-md);
                text-decoration: none;
                transition: background var(--transition-fast);
            }

            .patient-header__action:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
                text-decoration: none;
            }

            @media (max-width: 640px) {
                .patient-header {
                    flex-direction: column;
                    align-items: flex-start;
                }
            }
        """


def create_patient_header_from_data(patient_data: dict) -> PatientHeader:
    """Factory for creating PatientHeader from API response data."""
    return PatientHeader(
        first_name=patient_data.get("first_name", ""),
        last_name=patient_data.get("last_name", ""),
        date_of_birth=patient_data.get("date_of_birth"),
        gender=patient_data.get("gender"),
        patient_id=patient_data.get("id"),
    )
