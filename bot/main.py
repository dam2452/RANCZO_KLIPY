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
from bot.utils.log import get_log_level


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



logging.basicConfig(level=get_log_level())
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup() -> None:
    await DatabaseManager.init_pool(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )
    await DatabaseManager.init_db()

    admin_user_id = int(os.getenv("DEFAULT_ADMIN"))
    user_data = await bot.get_chat(admin_user_id)

    await DatabaseManager.set_default_admin(
        user_id=admin_user_id,
        username=user_data.username or "unknown",
        full_name=user_data.full_name or "Unknown User",
    )
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
    try:
        db_log_handler.loop = asyncio.get_running_loop()
    except RuntimeError:
        db_log_handler.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(db_log_handler.loop)
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
