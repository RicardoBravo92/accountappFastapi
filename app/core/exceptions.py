"""Domain exceptions for the application.

These exceptions are raised by the service layer and converted to HTTP responses
by the API layer. This decouples business logic from HTTP concerns.
"""


class DomainException(Exception):
    """Base exception for domain-level errors."""

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(message)


class NotFoundError(DomainException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(f"{resource} with id '{identifier}' not found", "NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class ConflictError(DomainException):
    """Raised when a resource conflict occurs (e.g., duplicate)."""

    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")


class ValidationError(DomainException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class UnauthorizedError(DomainException):
    """Raised when authentication is required but not provided."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenError(DomainException):
    """Raised when user lacks permission for an action."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN")


class BusinessRuleError(DomainException):
    """Raised when a business rule is violated."""

    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
