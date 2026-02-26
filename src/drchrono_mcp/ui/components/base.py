"""Base component class for DrChrono Healthcare UI.

All UI components inherit from BaseComponent which provides:
- HTML escaping for security
- Fluent builder pattern with method chaining
- Consistent CSS class generation
- Accessibility defaults
"""

from __future__ import annotations

import html
from abc import ABC, abstractmethod
from typing import Any, Self


class BaseComponent(ABC):
    """Abstract base class for all UI components.

    Provides common functionality:
    - HTML escaping via _escape()
    - CSS class accumulation
    - Attribute management
    - Builder pattern with Self return type

    Subclasses must implement build() to return HTML string.
    """

    def __init__(self, css_class: str = "", **attrs: Any) -> None:
        """Initialize component with optional CSS classes and attributes.

        Args:
            css_class: Space-separated CSS class names
            **attrs: HTML attributes (use underscore for hyphenated: data_id -> data-id)
        """
        self._classes: list[str] = css_class.split() if css_class else []
        self._attrs: dict[str, str] = {}
        self._children: list[str] = []

        for key, value in attrs.items():
            # Convert underscore to hyphen for data- attributes
            attr_name = key.replace("_", "-")
            self._attrs[attr_name] = str(value)

    def add_class(self, *classes: str) -> Self:
        """Add one or more CSS classes.

        Args:
            *classes: CSS class names to add

        Returns:
            Self for method chaining
        """
        for cls in classes:
            if cls and cls not in self._classes:
                self._classes.append(cls)
        return self

    def remove_class(self, *classes: str) -> Self:
        """Remove one or more CSS classes.

        Args:
            *classes: CSS class names to remove

        Returns:
            Self for method chaining
        """
        for cls in classes:
            if cls in self._classes:
                self._classes.remove(cls)
        return self

    def set_attr(self, name: str, value: str) -> Self:
        """Set an HTML attribute.

        Args:
            name: Attribute name (use underscore for hyphenated)
            value: Attribute value

        Returns:
            Self for method chaining
        """
        attr_name = name.replace("_", "-")
        self._attrs[attr_name] = str(value)
        return self

    def add_child(self, child: str | BaseComponent) -> Self:
        """Add a child element.

        Args:
            child: HTML string or another component

        Returns:
            Self for method chaining
        """
        if isinstance(child, BaseComponent):
            self._children.append(child.build())
        else:
            self._children.append(child)
        return self

    def add_children(self, children: list[str | BaseComponent]) -> Self:
        """Add multiple child elements.

        Args:
            children: List of HTML strings or components

        Returns:
            Self for method chaining
        """
        for child in children:
            self.add_child(child)
        return self

    @property
    def class_string(self) -> str:
        """Get combined CSS class string."""
        return " ".join(self._classes)

    @property
    def attr_string(self) -> str:
        """Get HTML attribute string."""
        parts = []
        if self._classes:
            parts.append(f'class="{self.class_string}"')
        for name, value in self._attrs.items():
            parts.append(f'{name}="{self._escape(value)}"')
        return " ".join(parts)

    @property
    def children_html(self) -> str:
        """Get concatenated children HTML."""
        return "".join(self._children)

    @staticmethod
    def _escape(text: Any) -> str:
        """Escape HTML special characters for safe rendering.

        Args:
            text: Value to escape

        Returns:
            HTML-escaped string
        """
        if text is None:
            return ""
        return html.escape(str(text))

    @abstractmethod
    def build(self) -> str:
        """Build and return the component's HTML string.

        Subclasses must implement this method.

        Returns:
            Complete HTML string for the component
        """
        pass

    def __str__(self) -> str:
        """Return built HTML when stringified."""
        return self.build()


class Fragment(BaseComponent):
    """A component that renders only its children without a wrapper element.

    Useful for grouping components without adding DOM nodes.
    """

    def build(self) -> str:
        """Render children without wrapper."""
        return self.children_html


class RawHtml(BaseComponent):
    """A component that renders raw HTML without escaping.

    Use with caution - only for trusted content like SVG icons.
    """

    def __init__(self, html_content: str) -> None:
        """Initialize with raw HTML content.

        Args:
            html_content: Raw HTML string (not escaped)
        """
        super().__init__()
        self._raw_html = html_content

    def build(self) -> str:
        """Render raw HTML."""
        return self._raw_html


class Div(BaseComponent):
    """A simple div wrapper component."""

    def build(self) -> str:
        """Render as a div element."""
        return f"<div {self.attr_string}>{self.children_html}</div>"


class Span(BaseComponent):
    """A simple span wrapper component."""

    def __init__(self, text: str = "", **kwargs: Any) -> None:
        """Initialize span with optional text content.

        Args:
            text: Text content (will be escaped)
            **kwargs: Passed to BaseComponent
        """
        super().__init__(**kwargs)
        if text:
            self._children.append(self._escape(text))

    def build(self) -> str:
        """Render as a span element."""
        return f"<span {self.attr_string}>{self.children_html}</span>"
