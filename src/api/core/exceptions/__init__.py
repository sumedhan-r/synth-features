"""Feature-specific custom exceptions."""

# Storage layer exceptions (2000-2999)
from src.api.core.exceptions.storage import (
    StringMeasureNotFoundHTTPException,
    StringSongNotFoundHTTPException,
)

# String business logic exceptions (3000-3999)
from src.api.core.exceptions.strings import StringSongNoMeasuresHTTPException

__all__ = [
    # Storage (2000-2999)
    "StringSongNotFoundHTTPException",
    "StringMeasureNotFoundHTTPException",
    # Strings Business Logic (3000-3999)
    "StringSongNoMeasuresHTTPException",
]
