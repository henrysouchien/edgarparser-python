"""Python SDK for the hosted EdgarParser API."""

from .client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, EdgarClient
from .errors import (
    EdgarAPIError,
    EdgarAuthError,
    EdgarError,
    EdgarNotFoundError,
    EdgarRateLimitError,
    EdgarTimeoutError,
    EdgarTransportError,
    EdgarValidationError,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "EdgarAPIError",
    "EdgarAuthError",
    "EdgarClient",
    "EdgarError",
    "EdgarNotFoundError",
    "EdgarRateLimitError",
    "EdgarTimeoutError",
    "EdgarTransportError",
    "EdgarValidationError",
    "__version__",
]

__version__ = "0.1.3"
