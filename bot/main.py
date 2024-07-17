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


def create_whitelist_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
    return [
        StartHandler(bot, _logger),
        SubscriptionStatusHandler(bot, _logger),
    ]


def create_subscribed_handlers(_logger: logging.Logger) -> List[BotMessageHandler]:
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


whitelist_handlers = create_whitelist_handlers(logger)
subscribed_handlers = create_subscribed_handlers(logger)
moderator_handlers = create_moderator_handlers(logger)
admin_handlers = create_admin_handlers(logger)

whitelist_commands = [command for handler in whitelist_handlers for command in handler.get_commands()]
subscribed_commands = [command for handler in subscribed_handlers for command in handler.get_commands()]
moderator_commands = [command for handler in moderator_handlers for command in handler.get_commands()]
admin_commands = [command for handler in admin_handlers for command in handler.get_commands()]

whitelist_middleware = WhitelistMiddleware(logger, whitelist_commands)
subscribed_middleware = SubscriberMiddleware(logger, subscribed_commands)
mod_middleware = ModeratorMiddleware(logger, moderator_commands)
admin_middleware = AdminMiddleware(logger, admin_commands)


async def on_startup() -> None:
    await DatabaseManager.init_db()
    await DatabaseManager.set_default_admin(os.getenv("DEFAULT_ADMIN"))
    logger.info("📦 Database initialized and default admin set. 📦")

    for handler in whitelist_handlers:
        handler.register(dp)

    for handler in subscribed_handlers:
        handler.register(dp)

    for handler in moderator_handlers:
        handler.register(dp)

    for handler in admin_handlers:
        handler.register(dp)

    logger.info("🔧 Handlers registered successfully. 🔧")

    dp.message.middleware.register(whitelist_middleware)
    dp.message.middleware.register(subscribed_middleware)
    dp.message.middleware.register(mod_middleware)
    dp.message.middleware.register(admin_middleware)

    logger.info("Middlewares registered successfully.")


async def main() -> None:
    await on_startup()
    logger.info("🚀 Bot started successfully.🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    db_log_handler = DBLogHandler()
    db_log_handler.loop = asyncio.get_event_loop()
    logging.getLogger().addHandler(db_log_handler)
    asyncio.run(main())
