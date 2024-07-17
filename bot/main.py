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
from bot.middlewares import *  # pylint: disable=wildcard-import, unused-wildcard-import
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

admin_middleware = AdminMiddleware(logger)
auth_middleware = AuthorizationMiddleware(logger)
mod_middleware = ModeratorMiddleware(logger)


def create_standard_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    middlewares = [
        auth_middleware,
    ]

    return [
        AdjustVideoClipHandler(bot, _logger, middlewares),
        ClipHandler(bot, _logger, middlewares),
        CompileClipsHandler(bot, _logger, middlewares),
        CompileSelectedClipsHandler(bot, _logger, middlewares),
        DeleteClipHandler(bot, _logger, middlewares),
        EpisodeListHandler(bot, _logger, middlewares),
        ManualClipHandler(bot, _logger, middlewares),
        MyClipsHandler(bot, _logger, middlewares),
        ReportIssueHandler(bot, _logger, middlewares),
        SaveClipHandler(bot, _logger, middlewares),
        SearchHandler(bot, _logger, middlewares),
        SearchListHandler(bot, _logger, middlewares),
        SelectClipHandler(bot, _logger, middlewares),
        SendClipHandler(bot, _logger, middlewares),
        StartHandler(bot, _logger, middlewares),
        SubscriptionStatusHandler(bot, _logger, middlewares),
        TranscriptionHandler(bot, logger, middlewares),
    ]


def create_moderator_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    middlewares = [
        auth_middleware,
        mod_middleware,
    ]

    return [
        AdminHelpHandler(bot, _logger, middlewares),
        ListAdminsHandler(bot, _logger, middlewares),
        ListModeratorsHandler(bot, _logger, middlewares),
        ListWhitelistHandler(bot, _logger, middlewares),
    ]


def create_admin_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    middlewares = [
        admin_middleware,
        auth_middleware,
    ]

    return [
        AddSubscriptionHandler(bot, _logger, middlewares),
        AddWhitelistHandler(bot, _logger, middlewares),
        RemoveSubscriptionHandler(bot, _logger, middlewares),
        RemoveWhitelistHandler(bot, _logger, middlewares),
        UpdateWhitelistHandler(bot, _logger, middlewares),
    ]


handlers: List[BotMessageHandler] = create_standard_handlers(logger) + create_moderator_handlers(logger) + create_admin_handlers(logger)


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
