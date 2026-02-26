"""Base CSS for DrChrono Healthcare UI.

Clean foundation: reset, typography, utilities, clinical severity classes.
Warm parchment palette with subtle paper texture. Designed for readability.
"""

from drchrono_mcp.ui.theme.tokens import get_theme_css


def generate_base_css() -> str:
    """Generate base CSS with reset, typography, and utilities."""
    return f"""
{get_theme_css()}

*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html {{
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

body {{
    font-family: var(--font-body);
    font-size: 0.9375rem;
    line-height: 1.5;
    color: var(--text-primary);
    background-color: var(--bg-primary);
    background-image:
        url("data:image/svg+xml,%3Csvg width='40' height='40' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-body);
    font-weight: 600;
    line-height: 1.25;
    color: var(--text-primary);
}}

h1 {{ font-size: 1.5rem; margin-bottom: var(--space-4); }}
h2 {{ font-size: 1.25rem; margin-bottom: var(--space-3); }}
h3 {{ font-size: 1.0625rem; margin-bottom: var(--space-2); }}
h4 {{ font-size: 0.9375rem; margin-bottom: var(--space-2); }}

p {{ margin-bottom: var(--space-3); }}

a {{
    color: var(--accent-primary);
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

button {{
    font-family: var(--font-body);
    font-size: 0.875rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
}}

.text-mono {{ font-family: var(--font-mono); font-size: 0.875em; }}
.text-primary {{ color: var(--text-primary); }}
.text-secondary {{ color: var(--text-secondary); }}
.text-tertiary {{ color: var(--text-tertiary); }}
.text-xs {{ font-size: 0.75rem; }}
.text-sm {{ font-size: 0.8125rem; }}
.text-base {{ font-size: 0.9375rem; }}

/* Clinical severity classes */
.severity-critical {{
    --severity-color: var(--critical);
    --severity-text: var(--critical-text);
    --severity-bg: var(--critical-bg);
    --severity-border: var(--critical-border);
}}
.severity-warning {{
    --severity-color: var(--warning);
    --severity-text: var(--warning-text);
    --severity-bg: var(--warning-bg);
    --severity-border: var(--warning-border);
}}
.severity-success {{
    --severity-color: var(--success);
    --severity-text: var(--success-text);
    --severity-bg: var(--success-bg);
    --severity-border: var(--success-border);
}}
.severity-info {{
    --severity-color: var(--info);
    --severity-text: var(--info-text);
    --severity-bg: var(--info-bg);
    --severity-border: var(--info-border);
}}
.severity-normal {{
    --severity-color: var(--text-secondary);
    --severity-text: var(--text-primary);
    --severity-bg: var(--bg-card);
    --severity-border: var(--border-primary);
}}

:focus-visible {{
    outline: 2px solid var(--border-focus);
    outline-offset: 2px;
}}

@media print {{
    body {{ background: white; color: black; }}
    .no-print {{ display: none !important; }}
}}
"""


def generate_component_css() -> str:
    """Generate CSS for common component patterns."""
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

.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: 2px var(--space-2);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    border-radius: var(--radius-sm);
    background: var(--severity-bg);
    color: var(--severity-text);
    border: 1px solid var(--severity-border);
    text-transform: uppercase;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    font-size: 0.8125rem;
    font-weight: 500;
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
}

.btn-primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
}

.btn-primary:hover {
    background: var(--accent-hover);
}

.clinical-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
}

.clinical-table th,
.clinical-table td {
    text-align: left;
    padding: var(--space-2) var(--space-3);
    border-bottom: 1px solid var(--border-secondary);
}

.clinical-table th {
    font-weight: 600;
    font-size: 0.6875rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-tertiary);
}

.clinical-table tbody tr:hover {
    background: var(--bg-hover);
}

.clinical-value {
    font-family: var(--font-mono);
    font-size: 0.9375rem;
    font-weight: 500;
}

.clinical-value__unit {
    font-size: 0.75em;
    color: var(--text-secondary);
    margin-left: 2px;
}

.empty-state {
    text-align: center;
    padding: var(--space-8);
    color: var(--text-tertiary);
    font-size: 0.8125rem;
}
"""


def generate_full_stylesheet() -> str:
    """Generate the complete stylesheet for the DrChrono UI."""
    return generate_base_css() + generate_component_css()
