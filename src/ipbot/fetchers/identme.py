"""IP fetching strategy using the ident.me API."""

import httpx

from ipbot.fetchers.base import FetchStrategy


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
            Exception: If the IP address cannot be fetched due to network
                      errors, timeouts, or invalid response format.
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.IDENTME_URL)
                response.raise_for_status()

                ip_address = response.text.strip()

                if not ip_address:
                    raise Exception("Invalid response format from ident.me: empty response")

                return ip_address

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch IP from ident.me: {e}") from e
        except Exception as e:
            if "Invalid response format" in str(e):
                raise
            raise Exception(f"Failed to fetch IP from ident.me: {e}") from e
