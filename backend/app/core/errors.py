"""Custom exceptions and error handling."""
from typing import Any


class CodeToQueryError(Exception):
    """Base exception for CodeToQuery application."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize base exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CodeToQueryError):
    """Validation error exception."""

    def __init__(self, message: str, field: str | None = None, details: dict[str, Any] | None = None) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            details: Additional error details
        """
        self.field = field
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(message, details)


class NotFoundError(CodeToQueryError):
    """Resource not found exception."""

    def __init__(self, resource: str, resource_id: Any | None = None, details: dict[str, Any] | None = None) -> None:
        """
        Initialize not found error.

        Args:
            resource: Resource type
            resource_id: Resource identifier
            details: Additional error details
        """
        self.resource = resource
        self.resource_id = resource_id
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        
        details = details or {}
        details["resource"] = resource
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(message, details)


class ConflictError(CodeToQueryError):
    """Resource conflict exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize conflict error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)


class DatabaseError(CodeToQueryError):
    """Database operation error exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize database error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)


class ExtractionError(CodeToQueryError):
    """SQL extraction error exception."""

    def __init__(self, message: str, file_path: str | None = None, details: dict[str, Any] | None = None) -> None:
        """
        Initialize extraction error.

        Args:
            message: Error message
            file_path: File path where error occurred
            details: Additional error details
        """
        self.file_path = file_path
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(message, details)


class AnalysisError(CodeToQueryError):
    """Analysis error exception."""

    def __init__(self, message: str, query_id: int | None = None, details: dict[str, Any] | None = None) -> None:
        """
        Initialize analysis error.

        Args:
            message: Error message
            query_id: Query identifier
            details: Additional error details
        """
        self.query_id = query_id
        details = details or {}
        if query_id:
            details["query_id"] = query_id
        super().__init__(message, details)


class ExternalServiceError(CodeToQueryError):
    """External service error exception."""

    def __init__(self, message: str, service: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize external service error.

        Args:
            message: Error message
            service: Service name
            details: Additional error details
        """
        self.service = service
        details = details or {}
        details["service"] = service
        super().__init__(message, details)
