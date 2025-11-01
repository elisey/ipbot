"""Main entry point for the Telegram IP bot application."""

import logging

from telegram.ext import Application, ApplicationBuilder

from ipbot.bot import setup_handlers
from ipbot.config import BotConfig
from ipbot.factory import create_fetchers
from ipbot.logger import setup_logging
from ipbot.orchestrator import ParallelFetchOrchestrator

logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Build and configure the Telegram bot application.

    Returns:
        Application: Configured Telegram bot application ready to run.
    """
    # Load configuration
    config = BotConfig()
    logger.info("Configuration loaded successfully")

    # Create IP fetchers for all strategies from config
    fetchers = create_fetchers(config)
    fether_names = (f.get_name() for f in fetchers)
    logger.info(f"IP fetchers initialized with strategies: {', '.join(fether_names)}")

    # Create orchestrator for parallel fetching
    orchestrator = ParallelFetchOrchestrator(fetchers)
    logger.info(f"Parallel fetch orchestrator created with {len(fetchers)} fetchers")

    # Build application
    application = ApplicationBuilder().token(config.telegram_token).build()

    # Store config and orchestrator in bot_data for access in handlers
    application.bot_data["config"] = config
    application.bot_data["orchestrator"] = orchestrator

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
