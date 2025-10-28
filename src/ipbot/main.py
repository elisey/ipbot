"""Main entry point for the Telegram IP bot application."""

import logging

from telegram.ext import Application, ApplicationBuilder

from ipbot.bot import setup_handlers
from ipbot.config import BotConfig
from ipbot.factory import create_fetcher
from ipbot.logger import setup_logging

logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Build and configure the Telegram bot application.

    Returns:
        Application: Configured Telegram bot application ready to run.
    """
    # Load configuration
    config = BotConfig()
    logger.info("Configuration loaded successfully")

    # Create IP fetcher using first strategy from config
    strategy_list = config.get_strategy_list()
    fetcher = create_fetcher(strategy_list[0])
    logger.info(f"IP fetcher initialized with strategy: {strategy_list[0]}")

    # Build application
    application = ApplicationBuilder().token(config.telegram_token).build()

    # Store config and fetcher in bot_data for access in handlers
    application.bot_data["config"] = config
    application.bot_data["fetcher"] = fetcher

    # Register command handlers
    setup_handlers(application)

    return application


def main() -> None:
    """Run the Telegram bot application.

    This is the main entry point that starts the bot using long polling.
    """
    logger.info("Starting Telegram IP Bot...")

    # Build the application
    application = build_application()

    # Start polling
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()

    logger.info("Bot shutdown complete")


if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Run the bot
    main()
