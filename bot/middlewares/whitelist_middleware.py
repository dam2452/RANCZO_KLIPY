from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
)

from aiogram.types import TelegramObject

from bot.database.database_manager import DatabaseManager
from bot.middlewares.bot_middleware import BotMiddleware


class WhitelistMiddleware(BotMiddleware):
    async def handle(
            self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        if event.from_user.username and await DatabaseManager.is_user_in_db(event.from_user.username):
            return await handler(event, data)

        await event.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
        self._logger.warning(f"Unauthorized access attempt by user: {event.from_user.username}")
