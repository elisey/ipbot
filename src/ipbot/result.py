"""Data models for IP fetching results."""

from dataclasses import dataclass


@dataclass
class FetcherResult:
    """Result from a single IP fetcher.

    Attributes:
        fetcher_name: Display name of the fetcher (from get_name()).
        success: True if the fetcher succeeded, False if it failed.
        ip: The IP address if successful, None if failed.
        error_type: Error category if failed ("Timeout", "Network error", etc.), None if successful.
    """

    fetcher_name: str
    success: bool
    ip: str | None = None
    error_type: str | None = None


@dataclass
class FetchResult:
    """Aggregated results from all IP fetchers.

    Attributes:
        results: List of individual fetcher results.
        consensus_ip: The consensus IP address if all successful fetchers agree, None otherwise.
        has_conflicts: True if successful fetchers returned different IP addresses.
    """

    results: list[FetcherResult]
    consensus_ip: str | None
    has_conflicts: bool
