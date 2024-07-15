import asyncio
import asyncio.selector_events
import logging
from logging import LogRecord
import os
from typing import (
    List,
    Optional,
)

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import *  # pylint: disable=wildcard-import
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.settings import Settings
from bot.utils.database import DatabaseManager

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


bot = Bot(token=Settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# fixme zmienic na liste middlewarow i przekazywac tamtym klasom w ctor
dp.update.middleware(AuthorizationMiddleware())
dp.update.middleware(ErrorHandlerMiddleware())


handlers: List[BotMessageHandler] = [
    AddSubscriptionHandler(bot),
    AddWhitelistHandler(bot),
    AdjustVideoClipHandler(bot),
    AdminHelpHandler(bot),
    ClipHandler(bot),
    CompileClipsHandler(bot),
    CompileSelectedClipsHandler(bot),
    DeleteClipHandler(bot),
    EpisodeListHandler(bot),
    ListAdminsHandler(bot),
    ListModeratorsHandler(bot),
    ListWhitelistHandler(bot),
    ManualClipHandler(bot),
    MyClipsHandler(bot),
    RemoveSubscriptionHandler(bot),
    RemoveWhitelistHandler(bot),
    ReportIssueHandler(bot),
    SaveClipHandler(bot),
    SearchHandler(bot),
    SearchListHandler(bot),
    SelectClipHandler(bot),
    SendClipHandler(bot),
    StartHandler(bot),
    SubscriptionStatusHandler(bot),
    TranscriptionHandler(bot),
    UpdateWhitelistHandler(bot),
]


async def on_startup() -> None:
    await DatabaseManager.init_db()
    await DatabaseManager.set_default_admin(os.getenv("DEFAULT_ADMIN"))
    logger.info("📦 Database initialized and default admin set. 📦")

    for handler in handlers:
        handler.register(dp)

    logger.info("🔧 Handlers registered successfully. 🔧")


async def main() -> None:
    await on_startup()
    logger.info("🚀 Bot started successfully.🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_log_handler = DBLogHandler()
    db_log_handler.loop = asyncio.get_event_loop()
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
