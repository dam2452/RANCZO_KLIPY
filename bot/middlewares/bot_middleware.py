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
    List,
    Optional,
)

from aiogram import BaseMiddleware
from aiogram.types import (
    Message,
    TelegramObject,
)

from bot.database.database_manager import DatabaseManager


class BotMiddleware(BaseMiddleware, ABC):
    def __init__(self, logger: logging.Logger, supported_commands: List[str]):
        self._logger = logger
        self.__supported_commands = supported_commands
        self._logger.info(f"({self.get_middleware_name()}) Supported commands: {self.__supported_commands}")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        if not isinstance(event, Message) or self.get_command_without_initial_slash(event) not in self.__supported_commands:
            return await handler(event, data)

        return await self.handle(handler, event, data)

    def get_middleware_name(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def get_command_without_initial_slash(event: TelegramObject) -> str:
        return event.text.split()[0][1:]

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
