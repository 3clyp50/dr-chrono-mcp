"""Clinical data table component.

A styled table for displaying structured clinical data:
- Sortable columns (optional)
- Row highlighting for abnormal values
- Responsive with horizontal scroll
- Accessible with proper table semantics
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from drchrono_mcp.ui.components.base import BaseComponent

CellAlignment = Literal["left", "center", "right"]


class Column:
    """Column definition for DataTable."""

    def __init__(
        self,
        key: str,
        header: str,
        width: str | None = None,
        align: CellAlignment = "left",
        formatter: Callable[[Any], str] | None = None,
        is_mono: bool = False,
        is_clinical_value: bool = False,
    ) -> None:
        """Initialize column definition.

        Args:
            key: Data key to access from row dict
            header: Column header text
            width: Optional CSS width (e.g., "120px", "20%")
            align: Text alignment
            formatter: Optional function to format cell value
            is_mono: Use monospace font (for codes, IDs)
            is_clinical_value: Style as clinical value (for lab results)
        """
        self.key = key
        self.header = header
        self.width = width
        self.align = align
        self.formatter = formatter
        self.is_mono = is_mono
        self.is_clinical_value = is_clinical_value


class DataTable(BaseComponent):
    """A styled table component for clinical data display.

    Features:
    - Column definitions with formatting
    - Row-level severity highlighting
    - Empty state handling
    - Responsive horizontal scrolling
    - Accessible table structure
    """

    def __init__(
        self,
        columns: list[Column],
        data: list[dict],
        row_severity_key: str | None = None,
        empty_message: str = "No data available",
        caption: str | None = None,
        striped: bool = True,
        hoverable: bool = True,
        compact: bool = False,
        css_class: str = "",
        **attrs: Any,
    ) -> None:
        """Initialize data table.

        Args:
            columns: List of Column definitions
            data: List of row data dicts
            row_severity_key: Key to check for row severity (value: critical/warning/etc.)
            empty_message: Message when data is empty
            caption: Optional table caption (for accessibility)
            striped: Alternate row backgrounds
            hoverable: Highlight rows on hover
            compact: Reduced padding
            css_class: Additional CSS classes
            **attrs: Additional HTML attributes
        """
        super().__init__(css_class, **attrs)
        self._columns = columns
        self._data = data
        self._row_severity_key = row_severity_key
        self._empty_message = empty_message
        self._caption = caption
        self._striped = striped
        self._hoverable = hoverable
        self._compact = compact

        self.add_class("clinical-table-wrapper")

    def _build_header(self) -> str:
        """Build table header row."""
        cells = []
        for col in self._columns:
            style_parts = []
            if col.width:
                style_parts.append(f"width: {col.width}")
            if col.align != "left":
                style_parts.append(f"text-align: {col.align}")

            style = f'style="{"; ".join(style_parts)}"' if style_parts else ""
            cells.append(f"<th {style}>{self._escape(col.header)}</th>")

        return f"<tr>{''.join(cells)}</tr>"

    def _build_cell(self, col: Column, row: dict) -> str:
        """Build a single table cell."""
        value = row.get(col.key, "")

        # Apply formatter if provided
        if col.formatter:
            try:
                display_value = col.formatter(value)
            except Exception:
                display_value = str(value) if value else ""
        else:
            display_value = str(value) if value else ""

        # Build cell classes
        classes = []
        if col.is_mono:
            classes.append("text-mono")
        if col.is_clinical_value:
            classes.append("clinical-value")

        # Check if cell has abnormal marker
        abnormal_key = f"{col.key}_abnormal"
        if row.get(abnormal_key) or row.get("abnormal"):
            classes.append("cell--abnormal")

        class_attr = f'class="{" ".join(classes)}"' if classes else ""

        # Alignment
        style = f'style="text-align: {col.align}"' if col.align != "left" else ""

        return f"<td {class_attr} {style}>{self._escape(display_value)}</td>"

    def _build_row(self, row: dict, index: int) -> str:
        """Build a table row."""
        cells = [self._build_cell(col, row) for col in self._columns]

        # Row classes
        classes = []

        # Severity from row data
        if self._row_severity_key:
            severity = row.get(self._row_severity_key)
            if severity:
                classes.append(f"row--{severity}")

        # Striping
        if self._striped and index % 2 == 1:
            classes.append("row--striped")

        class_attr = f'class="{" ".join(classes)}"' if classes else ""

        return f"<tr {class_attr}>{''.join(cells)}</tr>"

    def _build_empty_state(self) -> str:
        """Build empty state display."""
        colspan = len(self._columns)
        return f'''
            <tr>
                <td colspan="{colspan}" class="empty-state">
                    {self._escape(self._empty_message)}
                </td>
            </tr>
        '''

    def build(self) -> str:
        """Build the complete table HTML."""
        # Table classes
        table_classes = ["clinical-table"]
        if self._hoverable:
            table_classes.append("clinical-table--hoverable")
        if self._compact:
            table_classes.append("clinical-table--compact")

        # Caption
        caption_html = ""
        if self._caption:
            caption_html = f"<caption>{self._escape(self._caption)}</caption>"

        # Body rows
        if self._data:
            body_rows = "".join(self._build_row(row, i) for i, row in enumerate(self._data))
        else:
            body_rows = self._build_empty_state()

        styles = self._get_component_styles()

        return f'''
            <style>{styles}</style>
            <div {self.attr_string}>
                <table class="{" ".join(table_classes)}">
                    {caption_html}
                    <thead>
                        {self._build_header()}
                    </thead>
                    <tbody>
                        {body_rows}
                    </tbody>
                </table>
            </div>
        '''

    @staticmethod
    def _get_component_styles() -> str:
        """Get component-specific CSS."""
        return """
            .clinical-table-wrapper {
                overflow-x: auto;
                border-radius: var(--radius-md);
            }

            .clinical-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.875rem;
            }

            .clinical-table caption {
                padding: var(--space-2);
                font-size: 0.75rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-secondary);
                text-align: left;
            }

            .clinical-table th {
                font-family: var(--font-body);
                font-weight: 600;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-secondary);
                text-align: left;
                padding: var(--space-3);
                border-bottom: 2px solid var(--border-primary);
                background: var(--bg-elevated);
            }

            .clinical-table td {
                padding: var(--space-3);
                border-bottom: 1px solid var(--border-secondary);
                color: var(--text-primary);
            }

            .clinical-table--compact th,
            .clinical-table--compact td {
                padding: var(--space-2);
            }

            .clinical-table tbody tr:last-child td {
                border-bottom: none;
            }

            .clinical-table--hoverable tbody tr {
                transition: background var(--transition-fast);
            }

            .clinical-table--hoverable tbody tr:hover {
                background: var(--bg-hover);
            }

            .clinical-table .row--striped {
                background: var(--bg-elevated);
            }

            .clinical-table .row--striped:hover {
                background: var(--bg-hover);
            }

            /* Severity row styling */
            .clinical-table .row--critical {
                background: var(--critical-bg);
            }

            .clinical-table .row--critical:hover {
                background: rgba(248, 81, 73, 0.2);
            }

            .clinical-table .row--warning {
                background: var(--warning-bg);
            }

            .clinical-table .row--warning:hover {
                background: rgba(210, 153, 34, 0.2);
            }

            /* Cell styling */
            .clinical-table .cell--abnormal {
                color: var(--critical-text);
                font-weight: 600;
            }

            .clinical-table .clinical-value {
                font-family: var(--font-mono);
                font-weight: 500;
            }

            .clinical-table .empty-state {
                text-align: center;
                padding: var(--space-8);
                color: var(--text-secondary);
                font-style: italic;
            }
        """


# Common formatters
def format_date(value: Any) -> str:
    """Format date value to display format."""
    if not value:
        return ""
    return str(value)[:10]


def format_datetime(value: Any) -> str:
    """Format datetime value to display format."""
    if not value:
        return ""
    s = str(value)
    if "T" in s:
        return s.replace("T", " ")[:16]
    return s[:16]


def format_currency(value: Any) -> str:
    """Format currency value."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value) if value else ""


def format_clinical_value(unit: str = "") -> Callable[[Any], str]:
    """Create a formatter for clinical values with unit.

    Args:
        unit: Unit to append (e.g., "mg/dL")

    Returns:
        Formatter function
    """

    def formatter(value: Any) -> str:
        if not value and value != 0:
            return ""
        return f"{value} {unit}".strip()

    return formatter
