import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import settings  # Import settings
from bot.handlers import register_handlers
from bot.utils.db import DatabaseManager
from bot.middlewares.authorization import AuthorizationMiddleware  # Import AuthorizationMiddleware
from bot.middlewares.error_handler import ErrorHandlerMiddleware  # Import ErrorHandlerMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Add middlewares
dp.update.middleware(AuthorizationMiddleware())  # Register AuthorizationMiddleware
dp.update.middleware(ErrorHandlerMiddleware())  # Register ErrorHandlerMiddleware

async def on_startup():
    try:
        # Initialize the database
        await DatabaseManager.init_db()
        await DatabaseManager.set_default_admin(os.getenv("DEFAULT_ADMIN"))
        logger.info("📦 Database initialized and default admin set. 📦")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database or set default admin: {e} ❌")

    try:
        # Register all handlers
        await register_handlers(dp)
        logger.info("🔧 Handlers registered successfully. 🔧")
    except Exception as e:
        logger.error(f"❌ Failed to register handlers: {e} ❌")

async def main():
    try:
        await on_startup()
        logger.info("🚀 Bot started successfully.🚀")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot encountered an error: {e} ❌")

if __name__ == "__main__":
    asyncio.run(main())
