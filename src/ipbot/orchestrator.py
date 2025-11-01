"""Orchestrator for parallel IP fetching from multiple sources."""

import asyncio

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherHTTPError, FetcherParsingError
from ipbot.result import FetcherResult, FetchResult


class ParallelFetchOrchestrator:
    """Orchestrates parallel IP fetching from multiple fetcher strategies.

    This class runs all configured fetchers in parallel, collects their results,
    and determines consensus by comparing successful fetcher outputs.
    """

    def __init__(self, fetchers: list[FetchStrategy]):
        """Initialize the orchestrator with a list of fetcher strategies.

        Args:
            fetchers: List of FetchStrategy instances to run in parallel.
        """
        self.fetchers = fetchers

    async def fetch_all(self) -> FetchResult:
        """Execute all fetchers in parallel and aggregate results.

        Runs all fetchers concurrently, categorizes results and errors,
        and determines consensus IP by comparing successful results.

        Returns:
            FetchResult containing all individual results, consensus IP,
            and conflict status.
        """
        # Run all fetchers in parallel, capturing exceptions
        results_or_exceptions = await asyncio.gather(
            *[self._fetch_with_name(fetcher) for fetcher in self.fetchers],
            return_exceptions=True,
        )

        # Process results
        fetcher_results = []
        successful_ips = []

        for i, result_or_exception in enumerate(results_or_exceptions):
            fetcher = self.fetchers[i]
            fetcher_name = fetcher.get_name()

            if isinstance(result_or_exception, Exception):
                # Fetcher failed
                error_type = self._categorize_error(result_or_exception)
                fetcher_results.append(
                    FetcherResult(
                        fetcher_name=fetcher_name,
                        success=False,
                        error_type=error_type,
                    )
                )
            else:
                # Fetcher succeeded
                ip_address = result_or_exception
                fetcher_results.append(
                    FetcherResult(
                        fetcher_name=fetcher_name,
                        success=True,
                        ip=ip_address,
                    )
                )
                successful_ips.append(ip_address)

        # Determine consensus
        consensus_ip = None
        has_conflicts = False

        if successful_ips:
            # Check if all successful IPs are the same
            unique_ips = set(successful_ips)
            if len(unique_ips) == 1:
                # All successful fetchers agree
                consensus_ip = successful_ips[0]
            else:
                # Conflicting IPs
                has_conflicts = True

        return FetchResult(
            results=fetcher_results,
            consensus_ip=consensus_ip,
            has_conflicts=has_conflicts,
        )

    async def _fetch_with_name(self, fetcher: FetchStrategy) -> str:
        """Fetch IP from a single fetcher.

        This wrapper method exists to allow proper exception propagation
        in asyncio.gather.

        Args:
            fetcher: The fetcher strategy to execute.

        Returns:
            The IP address as a string.

        Raises:
            Exception: Any exception raised by the fetcher.
        """
        return await fetcher.get_ip()

    def _categorize_error(self, exception: Exception) -> str:
        """Categorize an exception into a simple error type.

        Args:
            exception: The exception to categorize.

        Returns:
            A simple error category string.
        """
        # Check for timeout exceptions
        if isinstance(exception, asyncio.TimeoutError):
            return "Timeout"

        # Check for fetcher-specific exceptions
        if isinstance(exception, FetcherParsingError):
            return "Parsing error"

        if isinstance(exception, FetcherHTTPError):
            return "Network error"

        # Generic error for unknown types
        return "Error"
