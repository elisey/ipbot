"""Telegram bot command handlers."""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ipbot.config import BotConfig
from ipbot.formatter import ResultFormatter
from ipbot.orchestrator import ParallelFetchOrchestrator

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command.

    Sends a greeting message and basic usage info.
    """
    logger.info("start command called")
    if not update.effective_user or not update.message:
        return

    config = context.bot_data.get("config")

    # Optional: customize reply for authorized user
    if config and update.effective_user.id == config.telegram_owner_id:
        await update.message.reply_text(
            "👋 Hello! You are authorized to use this bot.\n"
            "Use /ip to get the current public IP address."
        )
    else:
        await update.message.reply_text("Unauthorized")


async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ip command.

    Fetches the public IP address from all enabled fetchers and sends
    a formatted result to the user if they are authorized.

    Args:
        update: The incoming update containing the message.
        context: The context containing bot_data with config and orchestrator.
    """
    logger.info("ip command called")
    if not update.effective_user or not update.message:
        return

    config: BotConfig = context.bot_data["config"]
    orchestrator: ParallelFetchOrchestrator = context.bot_data["orchestrator"]

    # Check authorization
    if update.effective_user.id != config.telegram_owner_id:
        logger.warning(
            f"Unauthorized access attempt from user {update.effective_user.id} "
            f"(username: {update.effective_user.username})"
        )
        await update.message.reply_text("Unauthorized")
        return

    # Fetch IP addresses from all fetchers
    fetch_result = await orchestrator.fetch_all()

    # Format and send result
    reply_message = ResultFormatter().format(fetch_result)
    await update.message.reply_text(reply_message)

    logger.info(
        f"Successfully sent IP result to authorized user {update.effective_user.id} "
        f"(consensus: {fetch_result.consensus_ip}, conflicts: {fetch_result.has_conflicts})"
    )


def setup_handlers(application: Application) -> None:
    """Register command handlers with the application.

    Args:
        application: The Telegram Application instance to register handlers with.
    """
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ip", ip_command))
    logger.info("Registered /ip command handler")
