import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
)

from aiogram import BaseMiddleware
from aiogram.types import (
    Message,
    TelegramObject,
)

from bot.utils.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        if not isinstance(event, Message):
            return await handler(event, data)

        username = event.from_user.username
        if username and await DatabaseManager.is_user_authorized(username):
            return await handler(event, data)

        await event.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
        logger.warning(f"Unauthorized access attempt by user: {username}")
