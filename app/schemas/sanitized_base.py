"""Base sanitized models with automatic XSS prevention."""

from typing import Any
from pydantic import BaseModel, field_validator, BeforeValidator
from typing_extensions import Annotated

from app.core.sanitization import sanitize_string, sanitize_html


# Annotated types for common sanitized fields
SanitizedStr = Annotated[str, BeforeValidator(sanitize_string)]
SanitizedHtml = Annotated[str, BeforeValidator(lambda v: sanitize_html(v, allow_html=True))]


class SanitizedBaseModel(BaseModel):
    """Base model with automatic string sanitization."""

    @field_validator("*", mode="before")
    @classmethod
    def sanitize_strings(cls, value: Any) -> Any:
        """Automatically sanitize all string fields before validation."""
        if isinstance(value, str):
            return sanitize_string(value)
        elif isinstance(value, dict):
            return {k: sanitize_string(v) if isinstance(v, str) else v for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_string(v) if isinstance(v, str) else v for v in value]
        return value

    class Config:
        # Ensure sanitization runs before other validations
        validate_assignment = True