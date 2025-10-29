"""HTTP fetcher helper for making API requests with common error handling."""

import httpx

from ipbot.fetchers.exceptions import FetcherHTTPError


class HttpFetcher:
    """Helper class for making HTTP requests with common error handling.

    This class encapsulates the common HTTP request logic used by all IP
    fetching strategies, including timeout configuration, request execution,
    and standardized error handling.
    """

    def __init__(self, timeout: float = 3.0):
        """Initialize the HTTP fetcher with a timeout.

        Args:
            timeout: Request timeout in seconds. Defaults to 3.0.
        """
        self.timeout = timeout

    async def fetch(self, url: str, service_name: str) -> httpx.Response:
        """Fetch URL and return response with error handling.

        Args:
            url: The URL to fetch.
            service_name: The name of the service (for error messages).

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            FetcherHTTPError: If the request fails due to network errors,
                             timeouts, or HTTP errors.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response
        except httpx.HTTPError as e:
            raise FetcherHTTPError(f"Failed to fetch IP from {service_name}: {e}") from e
        except Exception as e:
            raise FetcherHTTPError(f"Failed to fetch IP from {service_name}: {e}") from e
