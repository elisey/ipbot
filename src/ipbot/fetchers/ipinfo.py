"""IP fetching strategy using the ipinfo.io API."""

import httpx

from ipbot.fetchers.base import FetchStrategy


class IpinfoStrategy(FetchStrategy):
    """Fetch public IP address using the ipinfo.io API.

    This strategy uses the ipinfo.io plain text API endpoint to fetch
    the public IP address with a 3-second timeout.
    """

    IPINFO_URL = "https://ipinfo.io/ip"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        """Fetch and return the public IP address from ipinfo.io.

        Returns:
            str: The public IP address as a string.

        Raises:
            Exception: If the IP address cannot be fetched due to network
                      errors, timeouts, or invalid response format.
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.IPINFO_URL)
                response.raise_for_status()

                ip_address = response.text.strip()

                if not ip_address:
                    raise Exception("Invalid response format from ipinfo.io: empty response")

                return ip_address

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch IP from ipinfo.io: {e}") from e
        except Exception as e:
            if "Invalid response format" in str(e):
                raise
            raise Exception(f"Failed to fetch IP from ipinfo.io: {e}") from e
