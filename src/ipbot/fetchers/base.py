"""Base strategy interface for IP address fetching."""

from abc import ABC, abstractmethod


class FetchStrategy(ABC):
    """Abstract base class for IP address fetching strategies.

    Each concrete strategy implements a different method for fetching
    the public IP address (e.g., different API providers, curl, etc.).
    """

    @abstractmethod
    async def get_ip(self) -> str:
        """Fetch and return the public IP address.

        Returns:
            str: The public IP address as a string.

        Raises:
            Exception: If the IP address cannot be fetched.
        """
        pass
