from abc import (
    ABC,
    abstractmethod,
)
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

from bot.database.database_manager import DatabaseManager


class BotMiddleware(BaseMiddleware, ABC):
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        if not isinstance(event, Message):
            return await handler(event, data)

        return await self.handle(handler, event, data)

    @abstractmethod
    async def handle(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        pass

    @staticmethod
    async def _does_user_have_moderator_privileges(username: str) -> bool:
        return await DatabaseManager.is_user_moderator(username) or await DatabaseManager.is_user_admin(username)

    @staticmethod
    async def _does_user_have_admin_privileges(username: str) -> bool:
        return await DatabaseManager.is_user_admin(username)
