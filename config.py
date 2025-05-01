import os
import logging

# Telegram Bot Token - get from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# Validate the token
if not TELEGRAM_TOKEN:
    logging.error("TELEGRAM_TOKEN environment variable is not set. Please set it to run the bot.")
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")
