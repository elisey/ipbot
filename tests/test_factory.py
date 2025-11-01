"""Tests for the IP fetcher factory."""

import pytest

from ipbot.config import BotConfig
from ipbot.factory import create_fetchers
from ipbot.fetchers.custom import CustomStrategy
from ipbot.fetchers.identme import IdentMeStrategy
from ipbot.fetchers.ifconfig import IfconfigStrategy
from ipbot.fetchers.ipify import IpifyStrategy
from ipbot.fetchers.ipinfo import IpinfoStrategy


class TestCreateFetchers:
    """Tests for the create_fetchers factory function."""

    def test_create_fetchers_with_all_keyword(self) -> None:
        """Test that 'all' keyword creates all available fetchers."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="all"
        )

        fetchers = create_fetchers(config)

        # Should return all 5 fetchers
        assert len(fetchers) == 5

        # Check that all expected types are present
        fetcher_types = {type(f) for f in fetchers}
        expected_types = {
            IpifyStrategy,
            IdentMeStrategy,
            IfconfigStrategy,
            IpinfoStrategy,
            CustomStrategy,
        }
        assert fetcher_types == expected_types

    def test_create_fetchers_with_single_strategy(self) -> None:
        """Test creating a single fetcher."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="ipify"
        )

        fetchers = create_fetchers(config)

        assert len(fetchers) == 1
        assert isinstance(fetchers[0], IpifyStrategy)

    def test_create_fetchers_with_multiple_strategies(self) -> None:
        """Test creating multiple specific fetchers."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="ipify,identme,ifconfig",
        )

        fetchers = create_fetchers(config)

        assert len(fetchers) == 3
        assert isinstance(fetchers[0], IpifyStrategy)
        assert isinstance(fetchers[1], IdentMeStrategy)
        assert isinstance(fetchers[2], IfconfigStrategy)

    def test_create_fetchers_preserves_order(self) -> None:
        """Test that fetchers are created in the specified order."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="ipinfo,ipify,identme",
        )

        fetchers = create_fetchers(config)

        assert len(fetchers) == 3
        assert isinstance(fetchers[0], IpinfoStrategy)
        assert isinstance(fetchers[1], IpifyStrategy)
        assert isinstance(fetchers[2], IdentMeStrategy)

    def test_create_fetchers_with_unknown_strategy(self) -> None:
        """Test that unknown strategy raises ValueError."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="ipify,unknown,identme",
        )

        with pytest.raises(ValueError, match="Unknown strategies: unknown"):
            create_fetchers(config)

    def test_create_fetchers_with_multiple_unknown_strategies(self) -> None:
        """Test error message with multiple unknown strategies."""
        config = BotConfig(
            telegram_token="test",
            telegram_owner_id=123,
            fetcher_strategy_order="foo,bar,ipify",
        )

        with pytest.raises(ValueError, match="Unknown strategies: (foo, bar|bar, foo)"):
            create_fetchers(config)

    def test_create_fetchers_error_message_shows_available(self) -> None:
        """Test that error message lists available strategies."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="invalid"
        )

        with pytest.raises(ValueError) as exc_info:
            create_fetchers(config)

        error_message = str(exc_info.value)
        assert "Available:" in error_message
        assert "ipify" in error_message
        assert "identme" in error_message
        assert "ifconfig" in error_message
        assert "ipinfo" in error_message
        assert "custom" in error_message

    def test_create_fetchers_with_custom_strategy(self) -> None:
        """Test creating custom fetcher."""
        config = BotConfig(
            telegram_token="test", telegram_owner_id=123, fetcher_strategy_order="custom"
        )

        fetchers = create_fetchers(config)

        assert len(fetchers) == 1
        assert isinstance(fetchers[0], CustomStrategy)

    def test_create_fetchers_default_config(self, monkeypatch, tmp_path) -> None:
        """Test with default config (should use 'all')."""

        # Create empty .env to prevent loading from project root
        env_file = tmp_path / ".env"
        env_file.write_text("TELEGRAM_TOKEN=test\nTELEGRAM_OWNER_ID=123\n")
        monkeypatch.chdir(tmp_path)

        config = BotConfig()

        fetchers = create_fetchers(config)

        # Default is 'all', so should get all 5 fetchers
        assert len(fetchers) == 5
