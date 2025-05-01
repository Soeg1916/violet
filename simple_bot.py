#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Telegram Bot Test
Basic functionality test to ensure the bot can respond to commands.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

# Enable detailed logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(f"Received /start command from {update.effective_user.id}")
    await update.message.reply_text("👋 Hello! This is a test message. The bot is working!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info(f"Received /help command from {update.effective_user.id}")
    await update.message.reply_text("This is a simple test bot to verify functionality.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logger.info(f"Received message: {update.message.text} from {update.effective_user.id}")
    await update.message.reply_text(f"You said: {update.message.text}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add debug logging for all updates
    async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log all updates."""
        logger.debug(f"Received update: {update}")
        # No need to return anything or send messages

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Echo all non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Add the logging handler last with a different group
    application.add_handler(MessageHandler(filters.ALL, log_update), group=999)

    # Add error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error."""
        logger.error("Exception while handling an update:", exc_info=context.error)
    
    application.add_error_handler(error_handler)
    
    # Run the bot until the user presses Ctrl-C
    logger.info("Starting simplified bot polling...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()