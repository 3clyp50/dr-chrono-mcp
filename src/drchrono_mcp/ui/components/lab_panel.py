"""Lab results panel component with trend visualization.

Displays laboratory results with:
- Value and reference range
- Abnormal value highlighting
- Optional Chart.js trend line
- Grouped by panel/category
"""

from __future__ import annotations

import json
from typing import Any

from drchrono_mcp.ui.components.base import BaseComponent
from drchrono_mcp.ui.components.card import ClinicalCard
from drchrono_mcp.ui.theme import get_icon


class LabPanel(BaseComponent):
    """A panel component for displaying lab results with trends.

    Features:
    - Critical/warning highlighting for abnormal values
    - Inline sparkline charts for trends
    - Reference range display
    - Monospace clinical values
    """

    def __init__(
        self,
        lab_results: list[dict],
        show_chart: bool = True,
        title: str = "Lab Results",
        show_empty_state: bool = True,
        compact: bool = False,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize lab panel.

        Args:
            lab_results: List of lab result dicts with keys:
                - name/test: Test name
                - value/result: Numeric or string value
                - unit: Unit of measurement
                - normal_range/reference_range: Reference range string
                - abnormal: Boolean flag
                - date/date_created: Result date
                - status: final/preliminary
            show_chart: Include trend chart when multiple results
            title: Panel title
            show_empty_state: Show message if no results
            compact: Reduced visual treatment
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._lab_results = lab_results
        self._show_chart = show_chart
        self._title = title
        self._show_empty_state = show_empty_state
        self._compact = compact

        self.add_class("lab-panel")

    def _is_abnormal(self, lab: dict) -> bool:
        """Determine if a lab value is abnormal."""
        if lab.get("abnormal"):
            return True
        # Could add logic to check value against reference range
        return False

    def _get_severity(self, lab: dict) -> str:
        """Get severity level for a lab result."""
        if self._is_abnormal(lab):
            # Check for critical values (this would be more sophisticated in production)
            return "critical"
        return "normal"

    def _build_lab_item(self, lab: dict, index: int) -> str:
        """Build a single lab result item."""
        name = lab.get("name") or lab.get("test") or lab.get("description", "Unknown Test")
        value = lab.get("value") or lab.get("result", "")
        unit = lab.get("unit", "")
        ref_range = lab.get("normal_range") or lab.get("reference_range", "")
        date = str(lab.get("date") or lab.get("date_created", ""))[:10]

        is_abnormal = self._is_abnormal(lab)
        abnormal_class = "lab-item--abnormal" if is_abnormal else ""
        stagger_class = f"stagger-{min(index + 1, 5)}"

        value_display = f"{value} {unit}".strip()
        if is_abnormal:
            value_display = f"⚠ {value_display}"

        ref_html = ""
        if ref_range:
            ref_html = f'<span class="lab-item__reference">Ref: {self._escape(ref_range)}</span>'

        return f"""
            <div class="lab-item {abnormal_class} animate-fade-in-up {stagger_class}">
                <div class="lab-item__header">
                    <span class="lab-item__name">{self._escape(name)}</span>
                    <span class="lab-item__date">{self._escape(date)}</span>
                </div>
                <div class="lab-item__value-row">
                    <span class="lab-item__value text-mono">{self._escape(value_display)}</span>
                    {ref_html}
                </div>
            </div>
        """

    def _build_chart(self) -> str:
        """Build Chart.js trend visualization."""
        if not self._show_chart or len(self._lab_results) < 2:
            return ""

        # Group by test name
        groups: dict[str, list[dict]] = {}
        for lab in self._lab_results:
            name = lab.get("name") or lab.get("test") or "Unknown"
            if name not in groups:
                groups[name] = []
            groups[name].append(lab)

        # Find groups with multiple results (for trending)
        trendable = {k: v for k, v in groups.items() if len(v) >= 2}
        if not trendable:
            return ""

        # Pick first trendable group
        test_name, values = next(iter(trendable.items()))

        # Sort by date
        values = sorted(values, key=lambda x: x.get("date", x.get("date_created", "")))

        # Build chart data
        labels = [str(v.get("date", v.get("date_created", "")))[:10] for v in values]
        data_points = []
        for v in values:
            try:
                data_points.append(float(v.get("value", v.get("result", 0))))
            except (ValueError, TypeError):
                data_points.append(0)

        chart_id = f"lab_chart_{hash(test_name) % 10000}"

        # Check for abnormal points
        point_colors = []
        for v in values:
            if v.get("abnormal"):
                point_colors.append("var(--critical)")
            else:
                point_colors.append("var(--accent-primary)")

        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": test_name,
                        "data": data_points,
                        "borderColor": "rgb(88, 166, 255)",
                        "backgroundColor": "rgba(88, 166, 255, 0.1)",
                        "pointBackgroundColor": point_colors,
                        "pointBorderColor": point_colors,
                        "pointRadius": 6,
                        "tension": 0.3,
                        "fill": True,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "title": {
                        "display": True,
                        "text": f"{test_name} Trend",
                        "color": "rgb(139, 148, 158)",
                        "font": {"size": 14},
                    },
                },
                "scales": {
                    "y": {
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                        "ticks": {"color": "rgb(139, 148, 158)"},
                    },
                    "x": {
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                        "ticks": {"color": "rgb(139, 148, 158)"},
                    },
                },
            },
        }

        config_json = json.dumps(config)

        return f'''
            <div class="lab-panel__chart">
                <canvas id="{chart_id}"></canvas>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                (function() {{
                    const ctx = document.getElementById('{chart_id}');
                    if (ctx) {{
                        new Chart(ctx, {config_json});
                    }}
                }})();
            </script>
        '''

    def _build_empty_state(self) -> str:
        """Build empty state display."""
        return f"""
            <div class="lab-panel__empty">
                {get_icon("flask", size=24)}
                <span>No lab results available</span>
            </div>
        """

    def build(self) -> str:
        """Build the lab panel HTML."""
        styles = self._get_component_styles()

        if not self._lab_results:
            if self._show_empty_state:
                content = self._build_empty_state()
            else:
                content = ""
            chart_html = ""
        else:
            items = "".join(self._build_lab_item(lab, i) for i, lab in enumerate(self._lab_results))
            content = f'<div class="lab-panel__items">{items}</div>'
            chart_html = self._build_chart()

        if self._compact:
            return f"""
                <style>{styles}</style>
                <div {self.attr_string}>
                    {chart_html}
                    {content}
                </div>
            """

        # Check for abnormal values
        has_abnormal = any(self._is_abnormal(lab) for lab in self._lab_results)
        severity = "warning" if has_abnormal else "normal"

        card = ClinicalCard(
            title=self._title,
            icon="flask",
            severity=severity,
            badge_text=f"{len(self._lab_results)} results",
        )
        card.add_child(chart_html + content)

        return f"""
            <style>{styles}</style>
            {card.build()}
        """

    @staticmethod
    def _get_component_styles() -> str:
        """Get component-specific CSS."""
        return """
            .lab-panel__chart {
                height: 200px;
                margin-bottom: var(--space-4);
                padding: var(--space-3);
                background: var(--bg-elevated);
                border-radius: var(--radius-md);
            }

            .lab-panel__items {
                display: flex;
                flex-direction: column;
                gap: var(--space-2);
            }

            .lab-item {
                padding: var(--space-3);
                background: var(--bg-elevated);
                border-radius: var(--radius-md);
                border-left: 3px solid var(--border-primary);
                transition: all var(--transition-fast);
            }

            .lab-item:hover {
                background: var(--bg-hover);
            }

            .lab-item--abnormal {
                border-left-color: var(--critical);
                background: var(--critical-bg);
            }

            .lab-item--abnormal:hover {
                background: rgba(248, 81, 73, 0.2);
            }

            .lab-item__header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--space-1);
            }

            .lab-item__name {
                font-weight: 500;
                color: var(--text-primary);
            }

            .lab-item__date {
                font-size: 0.75rem;
                color: var(--text-tertiary);
            }

            .lab-item__value-row {
                display: flex;
                align-items: baseline;
                gap: var(--space-3);
            }

            .lab-item__value {
                font-size: 1.125rem;
                font-weight: 600;
                color: var(--text-primary);
            }

            .lab-item--abnormal .lab-item__value {
                color: var(--critical-text);
            }

            .lab-item__reference {
                font-size: 0.75rem;
                color: var(--text-tertiary);
            }

            .lab-panel__empty {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: var(--space-3);
                padding: var(--space-6);
                color: var(--text-secondary);
            }
        """


def create_lab_panel_from_data(lab_results: list[dict]) -> LabPanel:
    """Factory for creating LabPanel from API response.

    Args:
        lab_results: Lab results list from DrChrono API

    Returns:
        Configured LabPanel component
    """
    return LabPanel(lab_results=lab_results)
