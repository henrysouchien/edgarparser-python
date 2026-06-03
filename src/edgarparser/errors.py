"""Typed exceptions for the EdgarParser SDK."""

from __future__ import annotations

from typing import Any, Mapping


class EdgarError(Exception):
    """Base exception for all SDK errors."""


class EdgarTimeoutError(EdgarError):
    """Raised when an API request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        *,
        request: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.request = dict(request or {})


class EdgarTransportError(EdgarError):
    """Raised when the HTTP transport fails before receiving a response."""

    def __init__(
        self,
        message: str,
        *,
        request: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.request = dict(request or {})


class EdgarAPIError(EdgarError):
    """Raised for API responses that are errors or cannot be parsed."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        error_type: str | None = None,
        details: Any | None = None,
        request_id: str | None = None,
        request: Mapping[str, Any] | None = None,
        response: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.error_type = error_type
        self.details = details
        self.request_id = request_id
        self.request = dict(request or {})
        self.response = dict(response or {})


class EdgarAuthError(EdgarAPIError):
    """Raised for authentication and authorization errors."""


class EdgarRateLimitError(EdgarAPIError):
    """Raised for rate-limit errors."""


class EdgarValidationError(EdgarAPIError):
    """Raised for request validation errors."""


class EdgarNotFoundError(EdgarAPIError):
    """Raised when the requested API resource is not found."""
