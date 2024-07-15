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

from bot.database.database_manager import DatabaseManager
from bot.handlers import *  # pylint: disable=wildcard-import
from bot.middlewares import *  # pylint: disable=wildcard-import
from bot.settings import Settings

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

middlewares: List[BotMiddleware] = [
    AuthorizationMiddleware(logger),
]

handlers: List[BotMessageHandler] = [
    AddSubscriptionHandler(bot, logger, middlewares),
    AddWhitelistHandler(bot, logger, middlewares),
    AdjustVideoClipHandler(bot, logger, middlewares),
    AdminHelpHandler(bot, logger, middlewares),
    ClipHandler(bot, logger, middlewares),
    CompileClipsHandler(bot, logger, middlewares),
    CompileSelectedClipsHandler(bot, logger, middlewares),
    DeleteClipHandler(bot, logger, middlewares),
    EpisodeListHandler(bot, logger, middlewares),
    ListAdminsHandler(bot, logger, middlewares),
    ListModeratorsHandler(bot, logger, middlewares),
    ListWhitelistHandler(bot, logger, middlewares),
    ManualClipHandler(bot, logger, middlewares),
    MyClipsHandler(bot, logger, middlewares),
    RemoveSubscriptionHandler(bot, logger, middlewares),
    RemoveWhitelistHandler(bot, logger, middlewares),
    ReportIssueHandler(bot, logger, middlewares),
    SaveClipHandler(bot, logger, middlewares),
    SearchHandler(bot, logger, middlewares),
    SearchListHandler(bot, logger, middlewares),
    SelectClipHandler(bot, logger, middlewares),
    SendClipHandler(bot, logger, middlewares),
    StartHandler(bot, logger, middlewares),
    SubscriptionStatusHandler(bot, logger, middlewares),
    TranscriptionHandler(bot, logger, middlewares),
    UpdateWhitelistHandler(bot, logger, middlewares),
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
    await dp.start_polling(bot, logger)


if __name__ == "__main__":
    db_log_handler = DBLogHandler()
    db_log_handler.loop = asyncio.get_event_loop()
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
