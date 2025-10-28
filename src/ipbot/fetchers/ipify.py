"""IP fetching strategy using the ipify.org API."""

import httpx

from ipbot.fetchers.base import FetchStrategy


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
            Exception: If the IP address cannot be fetched due to network
                      errors, timeouts, or invalid response format.
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.IPIFY_URL)
                response.raise_for_status()

                data = response.json()

                if "ip" not in data:
                    raise Exception(
                        f"Invalid response format from ipify: missing 'ip' field in {data}"
                    )

                return data["ip"]

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch IP from ipify: {e}") from e
        except Exception as e:
            if "Invalid response format" in str(e):
                raise
            raise Exception(f"Failed to fetch IP from ipify: {e}") from e
