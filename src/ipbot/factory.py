"""Factory for creating IP fetcher strategy instances."""

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.ipify import IpifyStrategy


def create_fetcher(strategy_name: str) -> FetchStrategy:
    """Create and return an IP fetcher strategy based on the strategy name.

    Args:
        strategy_name: The name of the strategy to create (e.g., "ipify").

    Returns:
        FetchStrategy: An instance of the requested fetcher strategy.

    Raises:
        ValueError: If the strategy name is unknown or not supported.
    """
    strategies = {
        "ipify": IpifyStrategy,
    }

    strategy_class = strategies.get(strategy_name)

    if strategy_class is None:
        raise ValueError(
            f"Unknown IP fetcher strategy: '{strategy_name}'. "
            f"Available strategies: {', '.join(strategies.keys())}"
        )

    return strategy_class()
