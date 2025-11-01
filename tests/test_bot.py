"""Tests for Telegram bot handlers."""

from unittest.mock import AsyncMock, Mock

import pytest
from telegram import Update, User
from telegram.ext import ContextTypes

from ipbot.bot import ip_command, setup_handlers
from ipbot.result import FetcherResult, FetchResult


class TestIpCommand:
    """Tests for the /ip command handler."""

    @pytest.mark.asyncio
    async def test_ip_command_authorized_user_success(self):
        """Test /ip command with authorized user returns IP address."""
        # Create mock update with authorized user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock orchestrator with successful result
        mock_orchestrator = AsyncMock()
        fetch_result = FetchResult(
            results=[
                FetcherResult(fetcher_name="ipify", success=True, ip="203.0.113.42"),
                FetcherResult(fetcher_name="identme", success=True, ip="203.0.113.42"),
            ],
            consensus_ip="203.0.113.42",
            has_conflicts=False,
        )
        mock_orchestrator.fetch_all.return_value = fetch_result

        # Create mock context
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "orchestrator": mock_orchestrator,
            "config": Mock(telegram_owner_id=123456789),
        }

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify orchestrator was called
        mock_orchestrator.fetch_all.assert_called_once()

        # Verify message was sent with formatted result
        expected_message = """🌐 IP address: 203.0.113.42

🟢 ipify
🟢 identme"""
        mock_update.message.reply_text.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_ip_command_unauthorized_user(self):
        """Test /ip command with unauthorized user returns error message."""
        # Create mock update with unauthorized user
        mock_user = Mock(spec=User)
        mock_user.id = 999999999  # Different from owner_id

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock context
        mock_orchestrator = AsyncMock()
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "orchestrator": mock_orchestrator,
            "config": Mock(telegram_owner_id=123456789),
        }

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify orchestrator was NOT called
        mock_orchestrator.fetch_all.assert_not_called()

        # Verify unauthorized message was sent
        mock_update.message.reply_text.assert_called_once_with("Unauthorized")

    @pytest.mark.asyncio
    async def test_ip_command_all_fetchers_fail(self):
        """Test /ip command handles all fetchers failing."""
        # Create mock update with authorized user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock orchestrator with all failures
        mock_orchestrator = AsyncMock()
        fetch_result = FetchResult(
            results=[
                FetcherResult(fetcher_name="ipify", success=False, error_type="Network error"),
                FetcherResult(fetcher_name="identme", success=False, error_type="Timeout"),
            ],
            consensus_ip=None,
            has_conflicts=False,
        )
        mock_orchestrator.fetch_all.return_value = fetch_result

        # Create mock context
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "orchestrator": mock_orchestrator,
            "config": Mock(telegram_owner_id=123456789),
        }

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify error message was sent showing all failures
        expected_message = """🌐 IP address: unknown

❌ ipify: Network error
❌ identme: Timeout"""
        mock_update.message.reply_text.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_ip_command_with_conflicts(self):
        """Test /ip command shows conflicts when fetchers disagree."""
        # Create mock update with authorized user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock orchestrator with conflicts
        mock_orchestrator = AsyncMock()
        fetch_result = FetchResult(
            results=[
                FetcherResult(fetcher_name="ipify", success=True, ip="198.51.100.1"),
                FetcherResult(fetcher_name="identme", success=True, ip="203.0.113.42"),
            ],
            consensus_ip=None,
            has_conflicts=True,
        )
        mock_orchestrator.fetch_all.return_value = fetch_result

        # Create mock context
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "orchestrator": mock_orchestrator,
            "config": Mock(telegram_owner_id=123456789),
        }

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify conflict message was sent
        expected_message = """🌐 IP address: unknown

🟡 ipify: 198.51.100.1
🟡 identme: 203.0.113.42"""
        mock_update.message.reply_text.assert_called_once_with(expected_message)


class TestSetupHandlers:
    """Tests for handler registration."""

    def test_setup_handlers_registers_ip_command(self):
        """Test that setup_handlers registers the /ip command handler."""
        from telegram.ext import CommandHandler

        mock_application = Mock()

        setup_handlers(mock_application)

        # Verify add_handler was called twice (for /start and /ip)
        assert mock_application.add_handler.call_count == 2

        # Verify both are CommandHandlers
        calls = mock_application.add_handler.call_args_list
        for call in calls:
            handler = call[0][0]
            assert isinstance(handler, CommandHandler)
