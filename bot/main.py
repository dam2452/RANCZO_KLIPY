import asyncio
from asyncio.selector_events import BaseSelectorEventLoop
import logging
from logging import LogRecord
import os
from typing import Optional

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import register_handlers
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.settings import settings
from bot.utils.database import DatabaseManager

# TODO loglevel from env
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBLogHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.loop: Optional[asyncio.selector_events.BaseSelectorEventLoop] = None

    def emit(self, record: LogRecord) -> None:
        if self.loop is not None:
            self.loop.create_task(self.log_to_db(record))

    async def log_to_db(self, record: LogRecord) -> None:
        log_message = self.format(record)
        await DatabaseManager.log_system_message(record.levelname, log_message)


# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Add middlewares
dp.update.middleware(AuthorizationMiddleware())
dp.update.middleware(ErrorHandlerMiddleware())


async def on_startup() -> None:
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


async def main() -> None:
    try:
        await on_startup()
        logger.info("🚀 Bot started successfully.🚀")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot encountered an error: {e} ❌")


if __name__ == "__main__":
    db_log_handler = DBLogHandler()
    db_log_handler.loop = asyncio.get_event_loop()
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
