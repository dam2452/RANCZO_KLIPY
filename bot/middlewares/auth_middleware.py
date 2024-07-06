import logging

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Awaitable

from bot.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data) -> Awaitable: # TO DO: Change return type
        if not isinstance(event, Message):
            return await handler(event, data)

        username = event.from_user.username
        if username and await DatabaseManager.is_user_authorized(username):
            return await handler(event, data)

        await event.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
        logger.warning(f"Unauthorized access attempt by user: {username}")
