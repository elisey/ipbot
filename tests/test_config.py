"""Tests for configuration loading."""

from pathlib import Path

from ipbot.config import BotConfig


class TestBotConfig:
    """Tests for BotConfig model."""

    def test_load_from_env_file(self, tmp_path: Path, monkeypatch) -> None:
        """Test loading configuration from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TELEGRAM_TOKEN=test_token\n"
            "TELEGRAM_OWNER_ID=12345\n"
            "FETCHER_STRATEGY_ORDER=ipify,curl\n"
        )

        monkeypatch.chdir(tmp_path)
        config = BotConfig()

        assert config.telegram_token == "test_token"
        assert config.telegram_owner_id == 12345
        assert config.fetcher_strategy_order == "ipify,curl"

    def test_load_with_defaults(self, tmp_path: Path, monkeypatch) -> None:
        """Test loading with only required fields uses defaults."""
        env_file = tmp_path / ".env"
        env_file.write_text("TELEGRAM_TOKEN=test_token\nTELEGRAM_OWNER_ID=12345\n")

        monkeypatch.chdir(tmp_path)
        config = BotConfig()

        assert config.telegram_token == "test_token"
        assert config.telegram_owner_id == 12345
        assert config.fetcher_strategy_order == "all"

    def test_get_strategy_list_default(self, monkeypatch, tmp_path: Path) -> None:
        """Test parsing default strategy list returns 'all'."""
        # Create empty .env to prevent loading from project root
        env_file = tmp_path / ".env"
        env_file.write_text("TELEGRAM_TOKEN=test\nTELEGRAM_OWNER_ID=123\n")
        monkeypatch.chdir(tmp_path)

        config = BotConfig()
        assert config.get_strategy_list() == ["all"]

    def test_get_strategy_list_single(self) -> None:
        """Test parsing single strategy."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="ipify"
        )
        assert config.get_strategy_list() == ["ipify"]

    def test_get_strategy_list_multiple(self) -> None:
        """Test parsing multiple strategies."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="ipify,curl,ifconfigme",
        )
        assert config.get_strategy_list() == ["ipify", "curl", "ifconfigme"]

    def test_get_strategy_list_with_spaces(self) -> None:
        """Test parsing strategies with spaces."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="ipify , curl , ifconfigme",
        )
        assert config.get_strategy_list() == ["ipify", "curl", "ifconfigme"]

    def test_get_strategy_list_with_trailing_comma(self) -> None:
        """Test parsing strategies with trailing comma."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="ipify,curl,"
        )
        assert config.get_strategy_list() == ["ipify", "curl"]
