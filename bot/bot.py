import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import register_handlers
from bot.utils.db import init_db, set_default_admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def on_startup():
    try:
        # Initialize the database
        await init_db()
        await set_default_admin(os.getenv("DEFAULT_ADMIN"))
        logger.info("📦 Database initialized and default admin set.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database or set default admin: {e}")

    try:
        # Register all handlers
        register_handlers(dp)
        logger.info("🔧 Handlers registered successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to register handlers: {e}")

async def main():
    try:
        await on_startup()
        logger.info("🚀 Bot started successfully.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot encountered an error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
