import json
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
)

from aiogram.types import TelegramObject

from bot.middlewares.bot_middleware import BotMiddleware


class AdminMiddleware(BotMiddleware):
    async def handle(
            self, handler: Callable[[TelegramObject, json], Awaitable[Any]], event: TelegramObject,
            data: json,
    ) -> Optional[Awaitable]:
        if event.from_user and await self._does_user_have_admin_privileges(event.from_user.id):
            return await handler(event, data)

        await event.answer("❌ Nie masz uprawnień admina.❌")
        self._logger.warning(f"Unauthorized admin access attempt by user: {event.from_user.id}")
