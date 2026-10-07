"""Input sanitization utilities for XSS prevention."""

import html
import re
from typing import Any

# Allowed HTML tags for rich text fields (if any)
ALLOWED_TAGS = frozenset(
    [
        "p", "br", "strong", "em", "u", "ol", "ul", "li",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "code", "pre",
    ]
)

# Tags that are never allowed
FORBIDDEN_TAGS = frozenset(
    [
        "script", "iframe", "object", "embed", "form", "input",
        "button", "select", "option", "textarea", "link", "style",
        "meta", "base", "frame", "frameset", "applet",
    ]
)


def sanitize_html(value: str, allow_html: bool = False) -> str:
    """Sanitize HTML content to prevent XSS.

    Args:
        value: Input string
        allow_html: If True, allows a limited set of safe HTML tags

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)

    if not allow_html:
        # Escape all HTML
        return html.escape(value)

    # Allow only safe tags, escape everything else
    # This is a simple implementation; for production consider using bleach
    def replace_tag(match):
        tag = match.group(1).lower()
        if tag in FORBIDDEN_TAGS:
            return html.escape(match.group(0))
        if tag not in ALLOWED_TAGS:
            return html.escape(match.group(0))
        return match.group(0)

    # Simple regex to find HTML tags
    sanitized = re.sub(r"</?(\w+)[^>]*>", replace_tag, value)

    # Also escape any remaining script-like patterns
    sanitized = re.sub(
        r"(?i)(javascript:|on\w+\s*=)",
        lambda m: html.escape(m.group(0)),
        sanitized,
    )

    return sanitized


def sanitize_string(value: str, max_length: int | None = None) -> str:
    """Sanitize a plain string input.

    Args:
        value: Input string
        max_length: Optional maximum length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Strip whitespace
    value = value.strip()

    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length]

    # Escape HTML entities
    value = html.escape(value)

    return value


def sanitize_dict(data: dict[str, Any], fields: list[str] | None = None) -> dict[str, Any]:
    """Sanitize string values in a dictionary.

    Args:
        data: Dictionary to sanitize
        fields: Optional list of field names to sanitize (None = all string fields)

    Returns:
        Sanitized dictionary
    """
    result = {}
    for key, value in data.items():
        if fields and key not in fields:
            result[key] = value
        elif isinstance(value, str):
            result[key] = sanitize_string(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, fields)
        elif isinstance(value, list):
            result[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
