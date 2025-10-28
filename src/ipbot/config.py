"""Bot configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    telegram_token: str
    telegram_owner_id: int
    fetcher_strategy_order: str = "ipify"
    server_reply_format: str = "🌐 Your public IP is: {ip}"

    def get_strategy_list(self) -> list[str]:
        return [s.strip() for s in self.fetcher_strategy_order.split(",") if s.strip()]
