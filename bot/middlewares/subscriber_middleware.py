import json
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
)

from aiogram.types import TelegramObject

from bot.database.database_manager import DatabaseManager
from bot.middlewares.bot_middleware import BotMiddleware


class SubscriberMiddleware(BotMiddleware):
    async def handle(
            self, handler: Callable[[TelegramObject, json], Awaitable[Any]], event: TelegramObject,
            data: json,
    ) -> Optional[Awaitable]:
        if event.from_user and await DatabaseManager.is_user_subscribed(event.from_user.id):
            return await handler(event, data)

        await event.answer("❌ Nie masz subskrypcji do korzystania z tego bota.❌")
        self._logger.warning(f"Unsubscribed access attempt by user: {event.from_user.id}")
