"""Allergy list component for critical patient safety information.

Displays allergies with prominent visual treatment:
- Critical severity styling by default
- Drug vs. environmental differentiation
- Reaction severity indicators
"""

from __future__ import annotations

from typing import Any

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.components.card import ClinicalCard
from drchrono_mcp.ui.theme import get_icon


class AllergyList(BaseComponent):
    """A list component for displaying patient allergies.

    Features:
    - Critical visual treatment (this is SAFETY information)
    - Severity indicators for each allergy
    - Reaction descriptions
    - Empty state for NKDA (No Known Drug Allergies)
    """

    def __init__(
        self,
        allergies: list[dict],
        show_empty_state: bool = True,
        compact: bool = False,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize allergy list.

        Args:
            allergies: List of allergy dicts with keys:
                - allergen/description: Allergen name
                - reaction: Reaction type
                - severity: Severity level (severe, moderate, mild)
                - status: active/inactive
                - notes: Optional notes
            show_empty_state: Show NKDA message if no allergies
            compact: Reduced visual treatment
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._allergies = allergies
        self._show_empty_state = show_empty_state
        self._compact = compact

        self.add_class("allergy-list")

    def _get_severity_class(self, severity: str | None) -> str:
        """Map severity string to CSS class."""
        if not severity:
            return "severity-warning"
        severity = severity.lower()
        if severity in ("severe", "high", "life-threatening"):
            return "severity-critical"
        if severity in ("moderate", "medium"):
            return "severity-warning"
        return "severity-info"

    def _build_allergy_item(self, allergy: dict, index: int) -> str:
        """Build a single allergy list item."""
        allergen = allergy.get("allergen") or allergy.get("description") or "Unknown"
        reaction = allergy.get("reaction", "")
        severity = allergy.get("severity", "")
        notes = allergy.get("notes", "")

        severity_class = self._get_severity_class(severity)
        stagger_class = f"stagger-{min(index + 1, 5)}"

        severity_badge = ""
        if severity:
            severity_badge = f"""
                <span class="allergy-item__severity {severity_class}">
                    {self._escape(severity)}
                </span>
            """

        reaction_html = ""
        if reaction:
            reaction_html = f"""
                <div class="allergy-item__reaction">
                    <strong>Reaction:</strong> {self._escape(reaction)}
                </div>
            """

        notes_html = ""
        if notes:
            notes_html = f"""
                <div class="allergy-item__notes">{self._escape(notes)}</div>
            """

        return f"""
            <li class="allergy-item {severity_class} animate-fade-in-up {stagger_class}">
                <div class="allergy-item__icon">
                    {get_icon("alert", size=20)}
                </div>
                <div class="allergy-item__content">
                    <div class="allergy-item__header">
                        <span class="allergy-item__name">{self._escape(allergen)}</span>
                        {severity_badge}
                    </div>
                    {reaction_html}
                    {notes_html}
                </div>
            </li>
        """

    def _build_empty_state(self) -> str:
        """Build NKDA empty state."""
        return f"""
            <div class="allergy-list__empty severity-success">
                {get_icon("check", size=24)}
                <span>No Known Drug Allergies (NKDA)</span>
            </div>
        """

    def build(self) -> str:
        """Build the allergy list HTML."""
        styles = self._get_component_styles()

        if not self._allergies:
            if self._show_empty_state:
                content = self._build_empty_state()
            else:
                content = ""
        else:
            items = "".join(self._build_allergy_item(a, i) for i, a in enumerate(self._allergies))
            content = f'<ul class="allergy-list__items">{items}</ul>'

        # Wrap in card if not compact
        if self._compact:
            return f"""
                <style>{styles}</style>
                <div {self.attr_string}>{content}</div>
            """

        card = ClinicalCard(
            title="Allergies",
            icon="alert",
            severity="critical" if self._allergies else "success",
            badge_text=f"{len(self._allergies)} documented" if self._allergies else "NKDA",
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
            .allergy-list__items {
                list-style: none;
                margin: 0;
                padding: 0;
            }

            .allergy-item {
                display: flex;
                align-items: flex-start;
                gap: var(--space-3);
                padding: var(--space-3);
                margin-bottom: var(--space-2);
                background: var(--severity-bg);
                border: 1px solid var(--severity-border);
                border-left: 3px solid var(--severity-color);
                border-radius: var(--radius-md);
            }

            .allergy-item:last-child {
                margin-bottom: 0;
            }

            .allergy-item__icon {
                flex-shrink: 0;
                color: var(--severity-color);
            }

            .allergy-item__content {
                flex: 1;
                min-width: 0;
            }

            .allergy-item__header {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                flex-wrap: wrap;
            }

            .allergy-item__name {
                font-weight: 600;
                color: var(--severity-text);
            }

            .allergy-item__severity {
                font-size: 0.75rem;
                font-weight: 500;
                padding: var(--space-1) var(--space-2);
                border-radius: var(--radius-full);
                background: var(--severity-color);
                color: var(--text-inverse);
            }

            .allergy-item__reaction {
                font-size: 0.875rem;
                color: var(--text-primary);
                margin-top: var(--space-1);
            }

            .allergy-item__notes {
                font-size: 0.75rem;
                color: var(--text-secondary);
                margin-top: var(--space-1);
                font-style: italic;
            }

            .allergy-list__empty {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: var(--space-3);
                padding: var(--space-4);
                background: var(--severity-bg);
                border: 1px solid var(--severity-border);
                border-radius: var(--radius-md);
                color: var(--severity-text);
                font-weight: 500;
            }
        """


def create_allergy_list_from_data(allergies_data: list[dict]) -> AllergyList:
    """Factory for creating AllergyList from API response.

    Args:
        allergies_data: Allergies list from DrChrono API

    Returns:
        Configured AllergyList component
    """
    return AllergyList(allergies=allergies_data)
