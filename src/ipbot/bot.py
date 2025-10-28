"""Telegram bot command handlers."""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

    Fetches the public IP address and sends it to the user if they are authorized.

    Args:
        update: The incoming update containing the message.
        context: The context containing bot_data with config and fetcher.
    """
    logger.info("ip command called")
    if not update.effective_user or not update.message:
        return

    config = context.bot_data["config"]
    fetcher = context.bot_data["fetcher"]

    # Check authorization
    if update.effective_user.id != config.telegram_owner_id:
        logger.warning(
            f"Unauthorized access attempt from user {update.effective_user.id} "
            f"(username: {update.effective_user.username})"
        )
        await update.message.reply_text("Unauthorized")
        return

    # Fetch IP address
    try:
        ip_address = await fetcher.get_ip()
        reply_message = config.server_reply_format.format(ip=ip_address)
        await update.message.reply_text(reply_message)
        logger.info(f"Successfully sent IP address to authorized user {update.effective_user.id}")
    except Exception as e:
        error_message = f"Could not fetch public IP — reason: {e}"
        await update.message.reply_text(error_message)
        logger.error(f"Failed to fetch IP address: {e}", exc_info=True)


def setup_handlers(application: Application) -> None:
    """Register command handlers with the application.

    Args:
        application: The Telegram Application instance to register handlers with.
    """
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ip", ip_command))
    logger.info("Registered /ip command handler")
