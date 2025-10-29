"""IP fetching strategy using the ident.me API."""

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherParsingError
from ipbot.fetchers.http_fetcher import HttpFetcher


class IdentMeStrategy(FetchStrategy):
    """Fetch public IP address using the ident.me API.

    This strategy uses the 4.ident.me plain text API endpoint to fetch
    the public IP address with a 3-second timeout.
    """

    IDENTME_URL = "https://4.ident.me/"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        """Fetch and return the public IP address from ident.me.

        Returns:
            str: The public IP address as a string.

        Raises:
            FetcherHTTPError: If the request fails due to network errors,
                             timeouts, or HTTP errors.
            FetcherParsingError: If the response format is invalid.
        """
        http_fetcher = HttpFetcher(timeout=self.TIMEOUT)
        response = await http_fetcher.fetch(self.IDENTME_URL, "ident.me")

        ip_address = response.text.strip()

        if not ip_address:
            raise FetcherParsingError("Invalid response format from ident.me: empty response")

        return ip_address
