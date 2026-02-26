"""Clinical SVG icons for the DrChrono Healthcare UI.

Inline SVG icons optimized for clinical displays:
- Consistent 24x24 viewBox for uniform sizing
- currentColor fill for theme-aware coloring
- Accessible with aria-hidden (decorative) or role="img" (semantic)
"""
# ruff: noqa: E501  # SVG path data can't be reasonably line-wrapped

from typing import Literal

IconName = Literal[
    "alert",
    "pill",
    "heartbeat",
    "flask",
    "calendar",
    "user",
    "clipboard",
    "stethoscope",
    "syringe",
    "chart",
    "search",
    "settings",
    "moon",
    "sun",
    "chevron-right",
    "chevron-down",
    "x",
    "check",
    "warning",
    "info",
    "phone",
    "mail",
    "building",
    "clock",
    "refresh",
    "logout",
    "sparkles",
    "message-circle",
    "send",
    "tool",
    "key",
]


# SVG icon paths (24x24 viewBox)
ICON_PATHS: dict[str, str] = {
    "alert": """<path fill="currentColor" d="M12 2L1 21h22L12 2zm0 3.99L19.53 19H4.47L12 5.99zM11 10v4h2v-4h-2zm0 6v2h2v-2h-2z"/>""",
    "pill": """<path fill="currentColor" d="M4.22 11.29l9.07-9.07a5.002 5.002 0 017.07 7.07l-9.07 9.07a5.002 5.002 0 01-7.07-7.07zm1.41 1.41a3 3 0 004.24 4.24l3.53-3.53-4.24-4.24-3.53 3.53z"/>""",
    "heartbeat": """<path fill="currentColor" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/><path fill="none" stroke="currentColor" stroke-width="2" d="M2 13h4l2-4 4 8 2-4h8"/>""",
    "flask": """<path fill="currentColor" d="M6 3v6l-4 8v2c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2v-2l-4-8V3H6zm2 0h8v6.12l3.45 6.88H4.55L8 9.12V3zm4 10a2 2 0 100 4 2 2 0 000-4z"/>""",
    "calendar": """<path fill="currentColor" d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2z"/>""",
    "user": """<path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>""",
    "clipboard": """<path fill="currentColor" d="M19 3h-4.18C14.4 1.84 13.3 1 12 1s-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 16H5V5h2v3h10V5h2v14z"/>""",
    "stethoscope": """<path fill="currentColor" d="M19 8c-1.66 0-3 1.34-3 3v4c0 2.21-1.79 4-4 4s-4-1.79-4-4V9.46c1.72-.45 3-2 3-3.87V3H9v2.59c0 1.02-.69 1.91-1.66 2.22L6 8.2V3H4v5.2l-1.34-.39A2.405 2.405 0 011 5.59V3H-1v2.59c0 1.87 1.28 3.42 3 3.87V15c0 3.31 2.69 6 6 6s6-2.69 6-6v-4c0-.55.45-1 1-1s1 .45 1 1v2h2v-2c0-1.66-1.34-3-3-3z"/><circle fill="currentColor" cx="19" cy="14" r="1"/>""",
    "syringe": """<path fill="currentColor" d="M11.15 15.18L9.73 13.77l1.41-1.41-1.41-1.41 1.41-1.41 1.41 1.41 1.41-1.41-1.41-1.41 1.41-1.41 1.41 1.41 1.41-1.41-1.41-1.41 2.83-2.83 1.41 1.41-7.07 7.07 1.41 1.41-2.12 2.12-1.41-1.41-1.41 1.41 1.41 1.41-2.12 2.12-4.24-4.24.71-.71zm8.49-11.31l-1.41-1.41-2.12 2.12 1.41 1.41-2.83 2.83-1.41-1.41-7.07 7.07L3.51 17.17l3.54 3.54 2.83-2.83-.71-.71 5.66-5.66 1.41 1.41 2.83-2.83-1.41-1.41 2.12-2.12 1.41 1.41 1.41-1.41-1.41-1.41z"/>""",
    "chart": """<path fill="currentColor" d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99l1.5 1.5z"/>""",
    "search": """<path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>""",
    "settings": """<path fill="currentColor" d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.488.488 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>""",
    "moon": """<path fill="currentColor" d="M12 3a9 9 0 109 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 01-4.4 2.26 5.403 5.403 0 01-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>""",
    "sun": """<path fill="currentColor" d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 00-1.41 0 .996.996 0 000 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 00-1.41 0 .996.996 0 000 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 000-1.41l-1.06-1.06zm1.06-10.96a.996.996 0 000-1.41.996.996 0 00-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36a.996.996 0 000-1.41.996.996 0 00-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>""",
    "chevron-right": """<path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>""",
    "chevron-down": """<path fill="currentColor" d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>""",
    "x": """<path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>""",
    "check": """<path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>""",
    "warning": """<path fill="currentColor" d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>""",
    "info": """<path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>""",
    "phone": """<path fill="currentColor" d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>""",
    "mail": """<path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>""",
    "building": """<path fill="currentColor" d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/>""",
    "clock": """<path fill="currentColor" d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>""",
    "refresh": """<path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>""",
    "logout": """<path fill="currentColor" d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>""",
    "sparkles": """<path fill="currentColor" d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path fill="currentColor" d="M5 3v4M19 17v4M3 5h4M17 19h4"/>""",
    "message-circle": """<path fill="currentColor" d="M12 3c5.5 0 10 3.58 10 8s-4.5 8-10 8c-1.24 0-2.43-.18-3.53-.5C5.55 21 2 21 2 21c2.33-2.33 2.7-3.9 2.75-4.5C3.05 15.07 2 13.13 2 11c0-4.42 4.5-8 10-8z"/>""",
    "send": """<path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>""",
    "tool": """<path fill="currentColor" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>""",
    "key": """<path fill="currentColor" d="M12.65 10C11.83 7.67 9.61 6 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6c2.61 0 4.83-1.67 5.65-4H17v4h4v-4h2v-4H12.65zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>""",
}


def get_icon(
    name: IconName,
    size: int = 24,
    css_class: str = "",
    aria_label: str | None = None,
) -> str:
    """Generate an inline SVG icon.

    Args:
        name: Icon name from IconName type
        size: Icon size in pixels (default 24)
        css_class: Additional CSS classes
        aria_label: Accessible label (if None, icon is decorative)

    Returns:
        SVG element string
    """
    path = ICON_PATHS.get(name, ICON_PATHS["info"])

    if aria_label:
        aria_attrs = f'role="img" aria-label="{aria_label}"'
    else:
        aria_attrs = 'aria-hidden="true"'

    class_attr = f'class="{css_class}"' if css_class else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" {class_attr} {aria_attrs}>{path}</svg>'''


def get_severity_icon(severity: str, size: int = 20) -> str:
    """Get the appropriate icon for a clinical severity level.

    Args:
        severity: One of 'critical', 'warning', 'success', 'info', 'normal'
        size: Icon size in pixels

    Returns:
        SVG element string with appropriate styling
    """
    icon_map = {
        "critical": ("alert", "icon-critical"),
        "warning": ("warning", "icon-warning"),
        "success": ("check", "icon-success"),
        "info": ("info", "icon-info"),
        "normal": ("clipboard", "icon-normal"),
    }

    icon_name, css_class = icon_map.get(severity, ("info", "icon-info"))
    return get_icon(icon_name, size=size, css_class=css_class)
