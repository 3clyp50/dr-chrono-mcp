"""Medication list component for active prescriptions.

Displays current medications with:
- Drug name, dose, and frequency
- Route and prescriber information
- Refill status indicators
"""

from __future__ import annotations

from typing import Any

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.components.card import ClinicalCard
from drchrono_mcp.ui.theme import get_icon


class MedicationList(BaseComponent):
    """A list component for displaying active medications.

    Features:
    - Clear dose and frequency display
    - Medication status indicators
    - Grouped by category (optional)
    - Monospace for clinical values
    """

    def __init__(
        self,
        medications: list[dict],
        show_empty_state: bool = True,
        compact: bool = False,
        show_prescriber: bool = False,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize medication list.

        Args:
            medications: List of medication dicts with keys:
                - name: Drug name
                - dose/dosage: Dose amount
                - frequency: Frequency (e.g., "twice daily")
                - route: Administration route
                - status: active/inactive/discontinued
                - prescriber: Prescriber name
                - start_date: When started
                - notes: Optional notes
            show_empty_state: Show message if no medications
            compact: Reduced visual treatment
            show_prescriber: Include prescriber information
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._medications = medications
        self._show_empty_state = show_empty_state
        self._compact = compact
        self._show_prescriber = show_prescriber

        self.add_class("medication-list")

    def _build_medication_item(self, med: dict, index: int) -> str:
        """Build a single medication item."""
        name = med.get("name", "Unknown Medication")
        dose = med.get("dose") or med.get("dosage", "")
        frequency = med.get("frequency", "")
        route = med.get("route", "")
        status = med.get("status", "active")
        notes = med.get("notes", "")

        stagger_class = f"stagger-{min(index + 1, 5)}"

        # Build dosage string
        dosage_parts = [p for p in [dose, frequency, route] if p]
        dosage_str = " · ".join(dosage_parts) if dosage_parts else "As directed"

        # Status indicator
        status_class = "med-status--active" if status == "active" else "med-status--inactive"

        prescriber_html = ""
        if self._show_prescriber and med.get("prescriber"):
            prescriber_html = f"""
                <div class="medication-item__prescriber">
                    Rx by: {self._escape(med["prescriber"])}
                </div>
            """

        notes_html = ""
        if notes:
            notes_html = f"""
                <div class="medication-item__notes">{self._escape(notes)}</div>
            """

        return f"""
            <li class="medication-item animate-fade-in-up {stagger_class}">
                <div class="medication-item__icon">
                    {get_icon("pill", size=20)}
                </div>
                <div class="medication-item__content">
                    <div class="medication-item__header">
                        <span class="medication-item__name">{self._escape(name)}</span>
                        <span class="medication-item__status {status_class}"></span>
                    </div>
                    <div class="medication-item__dosage text-mono">{self._escape(dosage_str)}</div>
                    {prescriber_html}
                    {notes_html}
                </div>
            </li>
        """

    def _build_empty_state(self) -> str:
        """Build empty state for no medications."""
        return f"""
            <div class="medication-list__empty">
                {get_icon("pill", size=24)}
                <span>No active medications</span>
            </div>
        """

    def build(self) -> str:
        """Build the medication list HTML."""
        styles = self._get_component_styles()

        if not self._medications:
            if self._show_empty_state:
                content = self._build_empty_state()
            else:
                content = ""
        else:
            # Filter to active by default
            active_meds = [
                m for m in self._medications if m.get("status", "active").lower() in ("active", "")
            ]

            items = "".join(self._build_medication_item(m, i) for i, m in enumerate(active_meds))
            content = f'<ul class="medication-list__items">{items}</ul>'

        if self._compact:
            return f"""
                <style>{styles}</style>
                <div {self.attr_string}>{content}</div>
            """

        active_count = len(
            [m for m in self._medications if m.get("status", "active").lower() in ("active", "")]
        )

        card = ClinicalCard(
            title="Active Medications",
            icon="pill",
            severity="info" if active_count > 0 else "normal",
            badge_text=f"{active_count} active",
        )
        card.add_child(content)

        return f"""
            <style>{styles}</style>
            {card.build()}
        """

    @staticmethod
    def _get_component_styles() -> str:
        """Get component-specific CSS."""
        return """
            .medication-list__items {
                list-style: none;
                margin: 0;
                padding: 0;
            }

            .medication-item {
                display: flex;
                align-items: flex-start;
                gap: var(--space-3);
                padding: var(--space-3);
                border-bottom: 1px solid var(--border-secondary);
                transition: background var(--transition-fast);
            }

            .medication-item:last-child {
                border-bottom: none;
            }

            .medication-item:hover {
                background: var(--bg-hover);
            }

            .medication-item__icon {
                flex-shrink: 0;
                color: var(--accent-primary);
            }

            .medication-item__content {
                flex: 1;
                min-width: 0;
            }

            .medication-item__header {
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }

            .medication-item__name {
                font-weight: 600;
                color: var(--text-primary);
            }

            .medication-item__status {
                width: 8px;
                height: 8px;
                border-radius: var(--radius-full);
            }

            .med-status--active {
                background: var(--success);
            }

            .med-status--inactive {
                background: var(--text-tertiary);
            }

            .medication-item__dosage {
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-top: var(--space-1);
            }

            .medication-item__prescriber {
                font-size: 0.75rem;
                color: var(--text-tertiary);
                margin-top: var(--space-1);
            }

            .medication-item__notes {
                font-size: 0.75rem;
                color: var(--text-secondary);
                margin-top: var(--space-1);
                font-style: italic;
            }

            .medication-list__empty {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: var(--space-3);
                padding: var(--space-6);
                color: var(--text-secondary);
            }
        """


def create_medication_list_from_data(medications_data: list[dict]) -> MedicationList:
    """Factory for creating MedicationList from API response.

    Args:
        medications_data: Medications list from DrChrono API

    Returns:
        Configured MedicationList component
    """
    return MedicationList(medications=medications_data)
