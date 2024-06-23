import logging
import os
from telebot import TeleBot
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.admin import register_admin_handlers
from bot.handlers.clip import register_clip_handlers
from bot.handlers.search import register_search_handlers
from bot.utils.db import init_db, set_default_admin
from bot.handlers.start import register_start_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize the database
init_db()
set_default_admin(os.getenv("DEFAULT_ADMIN"))

# Register handlers
register_admin_handlers(bot)
register_clip_handlers(bot)
register_search_handlers(bot)
register_start_handlers(bot)

if __name__ == "__main__":
    logger.info("Bot started")
    try:
        bot.infinity_polling(interval=0, timeout=25)
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
