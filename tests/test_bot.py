"""Tests for Telegram bot handlers."""

from unittest.mock import AsyncMock, Mock

import pytest
from telegram import Update, User
from telegram.ext import ContextTypes

from ipbot.bot import ip_command, setup_handlers


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

        # Create mock context
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "fetcher": AsyncMock(),
            "config": Mock(
                telegram_owner_id=123456789, server_reply_format="🌐 Your public IP is: {ip}"
            ),
        }
        mock_context.bot_data["fetcher"].get_ip.return_value = "203.0.113.42"

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify fetcher was called
        mock_context.bot_data["fetcher"].get_ip.assert_called_once()

        # Verify message was sent with formatted IP
        mock_update.message.reply_text.assert_called_once_with("🌐 Your public IP is: 203.0.113.42")

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
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "fetcher": AsyncMock(),
            "config": Mock(
                telegram_owner_id=123456789, server_reply_format="🌐 Your public IP is: {ip}"
            ),
        }

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify fetcher was NOT called
        mock_context.bot_data["fetcher"].get_ip.assert_not_called()

        # Verify unauthorized message was sent
        mock_update.message.reply_text.assert_called_once_with("Unauthorized")

    @pytest.mark.asyncio
    async def test_ip_command_fetcher_failure(self):
        """Test /ip command handles fetcher failure gracefully."""
        # Create mock update with authorized user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock context with failing fetcher
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "fetcher": AsyncMock(),
            "config": Mock(
                telegram_owner_id=123456789, server_reply_format="🌐 Your public IP is: {ip}"
            ),
        }
        mock_context.bot_data["fetcher"].get_ip.side_effect = Exception("Network error")

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify error message was sent
        mock_update.message.reply_text.assert_called_once_with(
            "Could not fetch public IP — reason: Network error"
        )

    @pytest.mark.asyncio
    async def test_ip_command_custom_reply_format(self):
        """Test /ip command uses custom reply format from config."""
        # Create mock update with authorized user
        mock_user = Mock(spec=User)
        mock_user.id = 123456789

        mock_update = Mock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = AsyncMock()

        # Create mock context with custom format
        mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot_data = {
            "fetcher": AsyncMock(),
            "config": Mock(telegram_owner_id=123456789, server_reply_format="IP: {ip}"),
        }
        mock_context.bot_data["fetcher"].get_ip.return_value = "198.51.100.1"

        # Call handler
        await ip_command(mock_update, mock_context)

        # Verify message was sent with custom format
        mock_update.message.reply_text.assert_called_once_with("IP: 198.51.100.1")


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
