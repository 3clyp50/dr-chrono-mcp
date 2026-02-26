"""Design tokens for DrChrono Healthcare UI.

A warm, restrained design system for clinical environments:
- Parchment-tan palette, easy on the eyes for long sessions
- Warm dark variant for low-light environments
- Single teal accent for interactive elements
- Clinical severity colors used only where medically meaningful
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ThemeTokens:
    """CSS custom property tokens for theming."""

    font_body: ClassVar[str] = (
        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    )
    font_mono: ClassVar[str] = "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace"

    font_imports: ClassVar[str] = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    """


# Warm light theme (default) — parchment/tan
LIGHT_TOKENS = {
    "--bg-primary": "#f5f0e8",
    "--bg-secondary": "#ece5d8",
    "--bg-card": "#faf7f2",
    "--bg-elevated": "#efe9dd",
    "--bg-hover": "#e3dacb",
    "--bg-active": "#d6ccbb",
    "--text-primary": "#2c2418",
    "--text-secondary": "#6b5e4f",
    "--text-tertiary": "#928675",
    "--text-inverse": "#faf7f2",
    "--border-primary": "#ddd5c8",
    "--border-secondary": "#ece5d8",
    "--border-focus": "#0d9488",
    "--critical": "#c0392b",
    "--critical-text": "#922b21",
    "--critical-bg": "rgba(192, 57, 43, 0.08)",
    "--critical-border": "rgba(192, 57, 43, 0.2)",
    "--warning": "#b7791f",
    "--warning-text": "#7c5e10",
    "--warning-bg": "rgba(183, 121, 31, 0.1)",
    "--warning-border": "rgba(183, 121, 31, 0.22)",
    "--success": "#1e7a5f",
    "--success-text": "#145c47",
    "--success-bg": "rgba(30, 122, 95, 0.08)",
    "--success-border": "rgba(30, 122, 95, 0.18)",
    "--info": "#5a7285",
    "--info-text": "#3e5567",
    "--info-bg": "rgba(90, 114, 133, 0.08)",
    "--info-border": "rgba(90, 114, 133, 0.18)",
    "--accent-primary": "#0d9488",
    "--accent-hover": "#0f766e",
    "--shadow-sm": "0 1px 2px rgba(44, 36, 24, 0.06)",
    "--shadow-md": "0 2px 8px rgba(44, 36, 24, 0.08)",
    "--shadow-lg": "0 4px 16px rgba(44, 36, 24, 0.1)",
    "--chart-1": "#0d9488",
    "--chart-2": "#c0392b",
    "--chart-3": "#1e7a5f",
    "--chart-4": "#b7791f",
    "--chart-5": "#5a7285",
    "--chart-6": "#928675",
    "--chart-grid": "#ddd5c8",
    "--chart-text": "#6b5e4f",
}

# Warm dark theme — for low-light environments
DARK_TOKENS = {
    "--bg-primary": "#1a1713",
    "--bg-secondary": "#221f1a",
    "--bg-card": "#221f1a",
    "--bg-elevated": "#2e2923",
    "--bg-hover": "#3d362d",
    "--bg-active": "#4d4538",
    "--text-primary": "#ece5d8",
    "--text-secondary": "#a69a88",
    "--text-tertiary": "#7d7264",
    "--text-inverse": "#1a1713",
    "--border-primary": "#332e27",
    "--border-secondary": "#29251f",
    "--border-focus": "#2dd4bf",
    "--critical": "#e74c3c",
    "--critical-text": "#f1a9a0",
    "--critical-bg": "rgba(231, 76, 60, 0.12)",
    "--critical-border": "rgba(231, 76, 60, 0.25)",
    "--warning": "#d4a843",
    "--warning-text": "#f0d78c",
    "--warning-bg": "rgba(212, 168, 67, 0.12)",
    "--warning-border": "rgba(212, 168, 67, 0.25)",
    "--success": "#27ae60",
    "--success-text": "#82d9a5",
    "--success-bg": "rgba(39, 174, 96, 0.12)",
    "--success-border": "rgba(39, 174, 96, 0.25)",
    "--info": "#7f9aad",
    "--info-text": "#a3bbc9",
    "--info-bg": "rgba(127, 154, 173, 0.12)",
    "--info-border": "rgba(127, 154, 173, 0.25)",
    "--accent-primary": "#2dd4bf",
    "--accent-hover": "#14b8a6",
    "--shadow-sm": "0 1px 2px rgba(0, 0, 0, 0.35)",
    "--shadow-md": "0 2px 8px rgba(0, 0, 0, 0.35)",
    "--shadow-lg": "0 4px 16px rgba(0, 0, 0, 0.45)",
    "--chart-1": "#2dd4bf",
    "--chart-2": "#e74c3c",
    "--chart-3": "#27ae60",
    "--chart-4": "#d4a843",
    "--chart-5": "#7f9aad",
    "--chart-6": "#a69a88",
    "--chart-grid": "#332e27",
    "--chart-text": "#a69a88",
}


def generate_css_variables(tokens: dict[str, str]) -> str:
    """Generate CSS custom property declarations from token dict."""
    lines = [f"    {key}: {value};" for key, value in tokens.items()]
    return "\n".join(lines)


def get_theme_css() -> str:
    """Generate complete theme CSS with light/dark mode support.

    Warm parchment is default. Dark mode activates via data-theme or system preference.
    """
    return f"""
{ThemeTokens.font_imports}

:root {{
{generate_css_variables(LIGHT_TOKENS)}

    --font-body: {ThemeTokens.font_body};
    --font-mono: {ThemeTokens.font_mono};

    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    --space-16: 4rem;

    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    --radius-xl: 12px;
    --radius-full: 9999px;

    --transition-fast: 120ms ease;
    --transition-normal: 200ms ease;
}}

[data-theme="dark"] {{
{generate_css_variables(DARK_TOKENS)}
}}

@media (prefers-color-scheme: dark) {{
    :root:not([data-theme]) {{
{generate_css_variables(DARK_TOKENS)}
    }}
}}
"""


SEVERITY_COLORS = {
    "critical": {
        "color": "var(--critical)",
        "text": "var(--critical-text)",
        "bg": "var(--critical-bg)",
        "border": "var(--critical-border)",
    },
    "warning": {
        "color": "var(--warning)",
        "text": "var(--warning-text)",
        "bg": "var(--warning-bg)",
        "border": "var(--warning-border)",
    },
    "success": {
        "color": "var(--success)",
        "text": "var(--success-text)",
        "bg": "var(--success-bg)",
        "border": "var(--success-border)",
    },
    "info": {
        "color": "var(--info)",
        "text": "var(--info-text)",
        "bg": "var(--info-bg)",
        "border": "var(--info-border)",
    },
    "normal": {
        "color": "var(--text-secondary)",
        "text": "var(--text-primary)",
        "bg": "var(--bg-card)",
        "border": "var(--border-primary)",
    },
}
