"""DrChrono Healthcare UI Theme System.

Professional design system for clinical environments:
- CSS custom properties for runtime theme switching
- Clinical severity color palette
- Clean typography with Inter and JetBrains Mono
- Inline SVG icons for clinical concepts
"""

from drchrono_mcp.ui.theme.base_styles import (
    generate_base_css,
    generate_component_css,
    generate_full_stylesheet,
)
from drchrono_mcp.ui.theme.icons import (
    ICON_PATHS,
    IconName,
    get_icon,
    get_severity_icon,
)
from drchrono_mcp.ui.theme.tokens import (
    DARK_TOKENS,
    LIGHT_TOKENS,
    SEVERITY_COLORS,
    ThemeTokens,
    get_theme_css,
)

__all__ = [
    "DARK_TOKENS",
    "LIGHT_TOKENS",
    "SEVERITY_COLORS",
    "ThemeTokens",
    "get_theme_css",
    "generate_base_css",
    "generate_component_css",
    "generate_full_stylesheet",
    "get_icon",
    "get_severity_icon",
    "IconName",
    "ICON_PATHS",
]
