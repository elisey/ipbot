"""Bot configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    telegram_token: str
    telegram_owner_id: int
    fetcher_strategy_order: str = "all"

    def get_strategy_list(self) -> list[str]:
        return [s.strip() for s in self.fetcher_strategy_order.split(",") if s.strip()]
