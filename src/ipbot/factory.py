"""Factory for creating IP fetcher strategy instances."""

from ipbot.config import BotConfig
from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.custom import CustomStrategy
from ipbot.fetchers.identme import IdentMeStrategy
from ipbot.fetchers.ifconfig import IfconfigStrategy
from ipbot.fetchers.ipify import IpifyStrategy
from ipbot.fetchers.ipinfo import IpinfoStrategy


def create_fetchers(config: BotConfig) -> list[FetchStrategy]:
    strategy_list = config.get_strategy_list()

    STRATEGIES = {
        "identme": IdentMeStrategy,
        "ifconfig": IfconfigStrategy,
        "ipify": IpifyStrategy,
        "ipinfo": IpinfoStrategy,
        "custom": CustomStrategy,
    }

    if strategy_list == ["all"]:
        return [cls() for cls in STRATEGIES.values()]

    unknown = set(strategy_list) - STRATEGIES.keys()
    if unknown:
        raise ValueError(
            f"Unknown strategies: {', '.join(unknown)}. Available: {', '.join(STRATEGIES.keys())}"
        )

    return [STRATEGIES[name]() for name in strategy_list]
