import logging
import os
from telebot import TeleBot
from bot.config import TELEGRAM_BOT_TOKEN
from .handlers import register_handlers
from bot.utils.db import init_db, set_default_admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize the database
init_db()
set_default_admin(os.getenv("DEFAULT_ADMIN"))

# Register all handlers
register_handlers(bot)

if __name__ == "__main__":
    logger.info("Bot started")
    try:
        bot.infinity_polling(interval=0, timeout=25)
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
