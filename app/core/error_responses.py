"""Standardized error response models following RFC 7807 Problem Details."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Individual error detail."""

    field: str | None = Field(None, description="Field name if validation error")
    message: str = Field(..., description="Human-readable error message")
    code: str | None = Field(None, description="Machine-readable error code")


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details response."""

    type: str = Field(
        ..., description="URI reference that identifies the problem type"
    )
    title: str = Field(..., description="Short, human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: str | None = Field(None, description="URI reference identifying the specific occurrence")
    errors: list[ErrorDetail] | None = Field(None, description="Additional error details")


def create_problem_response(
    request_path: str,
    status_code: int,
    title: str,
    detail: str,
    error_type: str = "about:blank",
    errors: list[ErrorDetail] | None = None,
) -> ProblemDetail:
    """Create a standardized problem detail response."""
    return ProblemDetail(
        type=f"https://api.accountapp.com/errors/{error_type}",
        title=title,
        status=status_code,
        detail=detail,
        instance=request_path,
        errors=errors,
    )
