import asyncio
import asyncio.selector_events
import logging
from logging import LogRecord
import os
from typing import Optional

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.fsm.storage.memory import MemoryStorage

from bot.database.database_manager import DatabaseManager
from bot.factory import create_all_factories
from bot.settings import settings


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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup() -> None:
    await DatabaseManager.init_db()
    await DatabaseManager.set_default_admin(os.getenv("DEFAULT_ADMIN"))
    logger.info("📦 Database initialized and default admin set. 📦")

    factories = create_all_factories(logger, bot)
    for factory in factories:
        factory.create_and_register(dp)

    logger.info("Handlers and middlewares registered successfully.")


async def main() -> None:
    await on_startup()
    logger.info("🚀 Bot started successfully.🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_log_handler = DBLogHandler()
    db_log_handler.loop = asyncio.get_event_loop()
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
