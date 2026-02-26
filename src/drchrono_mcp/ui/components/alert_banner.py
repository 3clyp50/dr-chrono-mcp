"""Alert banner component for critical clinical notifications.

Full-width banners for displaying urgent information:
- Critical alerts (drug interactions, allergies)
- Warnings (abnormal lab values)
- Informational notices (appointment reminders)
"""

from __future__ import annotations

from typing import Any, Literal

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.theme import get_icon

AlertType = Literal["critical", "warning", "info", "success"]


class AlertBanner(BaseComponent):
    """A full-width alert banner for urgent notifications.

    Features:
    - Prominent visual treatment matching severity
    - Optional dismissible behavior
    - Optional action buttons
    - Accessible with ARIA live regions for screen readers
    """

    def __init__(
        self,
        message: str,
        alert_type: AlertType = "info",
        title: str | None = None,
        details: list[str] | None = None,
        dismissible: bool = False,
        action_text: str | None = None,
        action_url: str | None = None,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize an alert banner.

        Args:
            message: Primary alert message
            alert_type: Type determines styling (critical, warning, info, success)
            title: Optional bold title above message
            details: Optional list of detail items
            dismissible: Whether banner can be dismissed
            action_text: Optional action button text
            action_url: URL for action button
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._message = message
        self._alert_type = alert_type
        self._title = title
        self._details = details or []
        self._dismissible = dismissible
        self._action_text = action_text
        self._action_url = action_url

        self.add_class("alert-banner", f"alert-banner--{alert_type}")

        # ARIA attributes for accessibility
        self.set_attr("role", "alert")
        if alert_type in ("critical", "warning"):
            self.set_attr("aria-live", "assertive")
        else:
            self.set_attr("aria-live", "polite")

    def _get_icon_name(self) -> str:
        """Get the appropriate icon for the alert type."""
        icon_map = {
            "critical": "alert",
            "warning": "warning",
            "info": "info",
            "success": "check",
        }
        return icon_map.get(self._alert_type, "info")

    def build(self) -> str:
        """Build the alert banner HTML."""
        icon_html = get_icon(self._get_icon_name(), size=24, css_class="alert-banner__icon")

        title_html = ""
        if self._title:
            title_html = f'<strong class="alert-banner__title">{self._escape(self._title)}</strong>'

        details_html = ""
        if self._details:
            items = "".join(f"<li>{self._escape(d)}</li>" for d in self._details[:5])
            details_html = f'<ul class="alert-banner__details">{items}</ul>'

        dismiss_html = ""
        if self._dismissible:
            dismiss_html = f"""
                <button class="alert-banner__dismiss" aria-label="Dismiss alert">
                    {get_icon("x", size=20)}
                </button>
            """

        action_html = ""
        if self._action_text and self._action_url:
            action_html = f'''
                <a href="{self._escape(self._action_url)}" class="alert-banner__action">
                    {self._escape(self._action_text)}
                    {get_icon("chevron-right", size=16)}
                </a>
            '''

        styles = self._get_component_styles()

        return f"""
            <style>{styles}</style>
            <div {self.attr_string}>
                <div class="alert-banner__icon-wrapper">
                    {icon_html}
                </div>
                <div class="alert-banner__content">
                    {title_html}
                    <p class="alert-banner__message">{self._escape(self._message)}</p>
                    {details_html}
                </div>
                {action_html}
                {dismiss_html}
            </div>
        """

    @staticmethod
    def _get_component_styles() -> str:
        """Get component-specific CSS."""
        return """
            .alert-banner {
                display: flex;
                align-items: flex-start;
                gap: var(--space-4);
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                background: var(--severity-bg);
                border: 1px solid var(--severity-border);
                border-left: 4px solid var(--severity-color);
                animation: fadeInDown var(--transition-normal) ease-out;
            }

            .alert-banner--critical {
                --severity-color: var(--critical);
                --severity-bg: var(--critical-bg);
                --severity-border: var(--critical-border);
                --severity-text: var(--critical-text);
                box-shadow: var(--glow-critical);
            }

            .alert-banner--warning {
                --severity-color: var(--warning);
                --severity-bg: var(--warning-bg);
                --severity-border: var(--warning-border);
                --severity-text: var(--warning-text);
                box-shadow: var(--glow-warning);
            }

            .alert-banner--info {
                --severity-color: var(--info);
                --severity-bg: var(--info-bg);
                --severity-border: var(--info-border);
                --severity-text: var(--info-text);
            }

            .alert-banner--success {
                --severity-color: var(--success);
                --severity-bg: var(--success-bg);
                --severity-border: var(--success-border);
                --severity-text: var(--success-text);
                box-shadow: var(--glow-success);
            }

            .alert-banner__icon-wrapper {
                flex-shrink: 0;
                color: var(--severity-color);
            }

            .alert-banner__content {
                flex: 1;
                min-width: 0;
            }

            .alert-banner__title {
                display: block;
                font-weight: 600;
                color: var(--severity-text);
                margin-bottom: var(--space-1);
            }

            .alert-banner__message {
                margin: 0;
                color: var(--text-primary);
                line-height: 1.5;
            }

            .alert-banner__details {
                margin: var(--space-2) 0 0;
                padding-left: var(--space-4);
                font-size: 0.875rem;
                color: var(--text-secondary);
            }

            .alert-banner__details li {
                margin: var(--space-1) 0;
            }

            .alert-banner__action {
                display: inline-flex;
                align-items: center;
                gap: var(--space-1);
                flex-shrink: 0;
                padding: var(--space-2) var(--space-3);
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--severity-text);
                background: transparent;
                border: 1px solid var(--severity-border);
                border-radius: var(--radius-md);
                text-decoration: none;
                transition: all var(--transition-fast);
            }

            .alert-banner__action:hover {
                background: var(--severity-color);
                color: var(--text-inverse);
                border-color: var(--severity-color);
            }

            .alert-banner__dismiss {
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
                background: transparent;
                border: none;
                border-radius: var(--radius-sm);
                color: var(--text-secondary);
                cursor: pointer;
                transition: all var(--transition-fast);
            }

            .alert-banner__dismiss:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
            }
        """


def create_critical_alert(
    message: str,
    title: str = "Critical Alert",
    details: list[str] | None = None,
) -> AlertBanner:
    """Factory for creating critical alerts (e.g., drug interactions)."""
    return AlertBanner(
        message=message,
        alert_type="critical",
        title=title,
        details=details,
    )


def create_warning_alert(
    message: str,
    title: str = "Warning",
    details: list[str] | None = None,
) -> AlertBanner:
    """Factory for creating warning alerts (e.g., abnormal lab values)."""
    return AlertBanner(
        message=message,
        alert_type="warning",
        title=title,
        details=details,
    )
