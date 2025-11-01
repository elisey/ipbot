"""IP fetching strategy using the ifconfig.me API."""

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherParsingError
from ipbot.fetchers.http_fetcher import HttpFetcher


class IfconfigStrategy(FetchStrategy):
    """Fetch public IP address using the ifconfig.me API.

    This strategy uses the ifconfig.me plain text API endpoint to fetch
    the public IP address with a 3-second timeout.
    """

    IFCONFIG_URL = "https://ifconfig.me/ip"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        """Fetch and return the public IP address from ifconfig.me.

        Returns:
            str: The public IP address as a string.

        Raises:
            FetcherHTTPError: If the request fails due to network errors,
                             timeouts, or HTTP errors.
            FetcherParsingError: If the response format is invalid.
        """
        http_fetcher = HttpFetcher(timeout=self.TIMEOUT)
        response = await http_fetcher.fetch(self.IFCONFIG_URL, self.get_name())

        ip_address = response.text.strip()

        if not ip_address:
            raise FetcherParsingError("Invalid response format from ifconfig.me: empty response")

        return ip_address

    def get_name(self) -> str:
        """Return the display name for this fetcher.

        Returns:
            str: The name "ifconfig".
        """
        return "ifconfig.me"
