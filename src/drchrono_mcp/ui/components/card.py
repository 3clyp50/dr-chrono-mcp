"""Clinical card component with severity indicators.

Cards are the primary container for clinical information with:
- Optional left-border severity indicator (critical/warning/success/info)
- Header with icon and title
- Collapsible content support
"""

from __future__ import annotations

from typing import Any, Literal, Self

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.theme import IconName, get_icon

Severity = Literal["critical", "warning", "success", "info", "normal"]


class ClinicalCard(BaseComponent):
    """A card component for displaying clinical information.

    Features:
    - Left-border severity indicator for visual triage
    - Optional header with icon and badge
    - Responsive and accessible design
    """

    def __init__(
        self,
        title: str | None = None,
        icon: IconName | None = None,
        severity: Severity = "normal",
        badge_text: str | None = None,
        collapsible: bool = False,
        collapsed: bool = False,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize a clinical card.

        Args:
            title: Card header title
            icon: Icon name for header (from theme.icons)
            severity: Severity level affects border color and glow
            badge_text: Optional badge next to title
            collapsible: Whether card content can be collapsed
            collapsed: Initial collapsed state (if collapsible)
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._title = title
        self._icon = icon
        self._severity = severity
        self._badge_text = badge_text
        self._collapsible = collapsible
        self._collapsed = collapsed
        self._header_actions: list[str] = []
        self._footer: str | None = None

        self.add_class("clinical-card")
        if severity != "normal":
            self.add_class("clinical-card--severity", f"severity-{severity}")

    def set_severity(self, severity: Severity) -> Self:
        """Update severity level.

        Args:
            severity: New severity level

        Returns:
            Self for chaining
        """
        # Remove old severity classes
        for sev in ("critical", "warning", "success", "info"):
            self.remove_class(f"severity-{sev}")
        if self._severity != "normal":
            self.remove_class("clinical-card--severity")

        # Add new severity
        self._severity = severity
        if severity != "normal":
            self.add_class("clinical-card--severity", f"severity-{severity}")
        return self

    def add_header_action(self, action_html: str) -> Self:
        """Add an action button/link to the header.

        Args:
            action_html: HTML for the action element

        Returns:
            Self for chaining
        """
        self._header_actions.append(action_html)
        return self

    def set_footer(self, footer_html: str) -> Self:
        """Set card footer content.

        Args:
            footer_html: HTML for the footer

        Returns:
            Self for chaining
        """
        self._footer = footer_html
        return self

    def _build_header(self) -> str:
        """Build the card header section."""
        if not self._title:
            return ""

        parts = []

        # Icon
        if self._icon:
            icon_html = get_icon(self._icon, size=20, css_class="card-header__icon")
            parts.append(f'<span class="card-header__icon-wrapper">{icon_html}</span>')

        # Title
        parts.append(f'<h3 class="card-header__title">{self._escape(self._title)}</h3>')

        # Badge
        if self._badge_text:
            badge_class = f"badge severity-{self._severity}"
            parts.append(f'<span class="{badge_class}">{self._escape(self._badge_text)}</span>')

        # Actions
        if self._header_actions:
            actions_html = "".join(self._header_actions)
            parts.append(f'<div class="card-header__actions">{actions_html}</div>')

        # Collapse toggle
        if self._collapsible:
            icon_name = "chevron-right" if self._collapsed else "chevron-down"
            chevron = get_icon(icon_name, size=16)
            expanded = "false" if self._collapsed else "true"
            parts.append(f'''
                <button class="card-header__toggle" aria-expanded="{expanded}">
                    {chevron}
                </button>
            ''')

        return f"""
            <div class="card-header">
                {"".join(parts)}
            </div>
        """

    def _build_content(self) -> str:
        """Build the card content section."""
        if not self._children:
            return ""

        collapsed_class = "card-content--collapsed" if self._collapsed else ""
        return f"""
            <div class="card-content {collapsed_class}">
                {self.children_html}
            </div>
        """

    def _build_footer(self) -> str:
        """Build the card footer section."""
        if not self._footer:
            return ""
        return f'<div class="card-footer">{self._footer}</div>'

    def build(self) -> str:
        """Build the complete card HTML."""
        # Add styles inline for self-contained components
        styles = self._get_component_styles()

        return f"""
            <style>{styles}</style>
            <article {self.attr_string}>
                {self._build_header()}
                {self._build_content()}
                {self._build_footer()}
            </article>
        """

    @staticmethod
    def _get_component_styles() -> str:
        return """
            .clinical-card {
                background: var(--bg-card);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-sm);
                overflow: hidden;
            }

            .clinical-card--severity {
                border-left: 3px solid var(--severity-color);
            }

            .card-header {
                display: flex;
                align-items: center;
                gap: var(--space-3);
                padding: var(--space-3) var(--space-4);
                border-bottom: 1px solid var(--border-secondary);
            }

            .card-header__icon-wrapper {
                display: flex;
                align-items: center;
                color: var(--severity-color, var(--text-tertiary));
            }

            .card-header__title {
                flex: 1;
                font-size: 0.8125rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.03em;
                margin: 0;
                color: var(--text-secondary);
            }

            .card-header__actions {
                display: flex;
                gap: var(--space-2);
            }

            .card-header__toggle {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                background: transparent;
                border: none;
                border-radius: var(--radius-sm);
                color: var(--text-tertiary);
                cursor: pointer;
            }

            .card-header__toggle:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
            }

            .card-content {
                padding: var(--space-4);
            }

            .card-content--collapsed {
                display: none;
            }

            .card-footer {
                padding: var(--space-3) var(--space-4);
                border-top: 1px solid var(--border-secondary);
                background: var(--bg-elevated);
            }
        """


class StatCard(BaseComponent):
    """A compact card for displaying a single statistic/metric.

    Used for KPIs, counts, and quick-glance data.
    """

    def __init__(
        self,
        label: str,
        value: str | int | float,
        unit: str | None = None,
        icon: IconName | None = None,
        severity: Severity = "normal",
        trend: Literal["up", "down", "flat"] | None = None,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize a stat card.

        Args:
            label: Metric label
            value: Metric value
            unit: Optional unit (e.g., "mg/dL", "bpm")
            icon: Optional icon
            severity: Severity coloring
            trend: Optional trend indicator
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._label = label
        self._value = value
        self._unit = unit
        self._icon = icon
        self._severity = severity
        self._trend = trend

        self.add_class("stat-card", f"severity-{severity}")

    def build(self) -> str:
        """Build the stat card HTML."""
        icon_html = ""
        if self._icon:
            icon_html = f"""
                <div class="stat-card__icon">
                    {get_icon(self._icon, size=24)}
                </div>
            """

        unit_html = ""
        if self._unit:
            unit_html = f'<span class="stat-card__unit">{self._escape(self._unit)}</span>'

        trend_html = ""
        if self._trend:
            trend_icon = "chevron-up" if self._trend == "up" else "chevron-down"
            if self._trend == "flat":
                trend_icon = "chevron-right"
            trend_html = f"""
                <span class="stat-card__trend stat-card__trend--{self._trend}">
                    {get_icon(trend_icon, size=16)}
                </span>
            """

        styles = """
            <style>
                .stat-card {
                    background: var(--bg-card);
                    border: 1px solid var(--border-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-4);
                    display: flex;
                    align-items: flex-start;
                    gap: var(--space-3);
                }

                .stat-card__icon {
                    color: var(--severity-color, var(--accent-primary));
                }

                .stat-card__content {
                    flex: 1;
                }

                .stat-card__label {
                    font-size: 0.75rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: var(--text-secondary);
                    margin-bottom: var(--space-1);
                }

                .stat-card__value {
                    font-family: var(--font-mono);
                    font-size: 1.75rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    line-height: 1;
                }

                .stat-card__unit {
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                    margin-left: var(--space-1);
                }

                .stat-card__trend {
                    display: inline-flex;
                    margin-left: var(--space-2);
                }

                .stat-card__trend--up { color: var(--success); }
                .stat-card__trend--down { color: var(--critical); }
                .stat-card__trend--flat { color: var(--text-secondary); }
            </style>
        """

        return f"""
            {styles}
            <div {self.attr_string}>
                {icon_html}
                <div class="stat-card__content">
                    <div class="stat-card__label">{self._escape(self._label)}</div>
                    <div class="stat-card__value">
                        {self._escape(str(self._value))}{unit_html}{trend_html}
                    </div>
                </div>
            </div>
        """
