"""Custom exceptions for IP fetcher operations."""


class FetcherException(Exception):
    """Base exception for all fetcher-related errors."""

    pass


class FetcherHTTPError(FetcherException):
    """Raised when an HTTP request fails due to network or HTTP errors."""

    pass


class FetcherParsingError(FetcherException):
    """Raised when response parsing or validation fails."""

    pass
