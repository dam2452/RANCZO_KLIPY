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


def create_standard_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    return [
        AdjustVideoClipHandler(bot, _logger),
        ClipHandler(bot, _logger),
        CompileClipsHandler(bot, _logger),
        CompileSelectedClipsHandler(bot, _logger),
        DeleteClipHandler(bot, _logger),
        EpisodeListHandler(bot, _logger),
        ManualClipHandler(bot, _logger),
        MyClipsHandler(bot, _logger),
        ReportIssueHandler(bot, _logger),
        SaveClipHandler(bot, _logger),
        SearchHandler(bot, _logger),
        SearchListHandler(bot, _logger),
        SelectClipHandler(bot, _logger),
        SendClipHandler(bot, _logger),
        StartHandler(bot, _logger),
        SubscriptionStatusHandler(bot, _logger),
        TranscriptionHandler(bot, _logger),
    ]


def create_moderator_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    return [
        AdminHelpHandler(bot, _logger),
        ListAdminsHandler(bot, _logger),
        ListModeratorsHandler(bot, _logger),
        ListWhitelistHandler(bot, _logger),
    ]


def create_admin_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    return [
        AddSubscriptionHandler(bot, _logger),
        AddWhitelistHandler(bot, _logger),
        RemoveSubscriptionHandler(bot, _logger),
        RemoveWhitelistHandler(bot, _logger),
        UpdateWhitelistHandler(bot, _logger),
    ]


standard_handlers = create_standard_handlers(logger)
moderator_handlers = create_moderator_handlers(logger)
admin_handlers = create_admin_handlers(logger)

moderator_commands = [command for handler in moderator_handlers for command in handler.get_commands()]
standard_commands = [command for handler in standard_handlers for command in handler.get_commands()]
admin_commands = [command for handler in admin_handlers for command in handler.get_commands()]

admin_middleware = AdminMiddleware(logger, admin_commands)
auth_middleware = AuthorizationMiddleware(logger, standard_commands + moderator_commands + admin_commands)
mod_middleware = ModeratorMiddleware(logger, moderator_commands)


async def on_startup() -> None:
    await DatabaseManager.init_db()
    await DatabaseManager.set_default_admin(os.getenv("DEFAULT_ADMIN"))
    logger.info("📦 Database initialized and default admin set. 📦")

    for handler in standard_handlers:
        handler.register(dp, [auth_middleware])

    for handler in moderator_handlers:
        handler.register(dp, [mod_middleware, auth_middleware])

    for handler in admin_handlers:
        handler.register(dp, [admin_middleware, auth_middleware])

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
