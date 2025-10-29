"""IP fetching strategy using the ipify.org API."""

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherParsingError
from ipbot.fetchers.http_fetcher import HttpFetcher


class IpifyStrategy(FetchStrategy):
    """Fetch public IP address using the ipify.org API.

    This strategy uses the ipify.org JSON API endpoint to fetch
    the public IP address with a 3-second timeout.
    """

    IPIFY_URL = "https://api.ipify.org?format=json"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        """Fetch and return the public IP address from ipify.org.

        Returns:
            str: The public IP address as a string.

        Raises:
            FetcherHTTPError: If the request fails due to network errors,
                             timeouts, or HTTP errors.
            FetcherParsingError: If the response format is invalid.
        """
        http_fetcher = HttpFetcher(timeout=self.TIMEOUT)
        response = await http_fetcher.fetch(self.IPIFY_URL, "ipify")

        data = response.json()

        if "ip" not in data:
            raise FetcherParsingError(
                f"Invalid response format from ipify: missing 'ip' field in {data}"
            )

        return data["ip"]
