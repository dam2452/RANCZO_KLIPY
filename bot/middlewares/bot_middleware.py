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
from bot.responses.bot_message_handler_responses import get_limit_exceeded_message
from bot.settings import settings


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
    async def _does_user_have_moderator_privileges(user_id: int) -> bool:
        return await DatabaseManager.is_user_moderator(user_id) or await DatabaseManager.is_user_admin(user_id)

    @staticmethod
    async def _does_user_have_admin_privileges(user_id: int) -> bool:
        return await DatabaseManager.is_user_admin(user_id)

    @staticmethod
    async def _check_command_limits_and_privileges(event: Message) -> bool:
        user_id = event.from_user.id
        is_admin_or_moderator = await DatabaseManager.is_admin_or_moderator(user_id)

        if not is_admin_or_moderator and await DatabaseManager.is_command_limited(user_id, settings.MESSAGE_LIMIT, settings.LIMIT_DURATION):
            await event.answer(get_limit_exceeded_message())
            return False

        return True
