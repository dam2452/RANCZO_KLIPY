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


class AnyMiddleware(BaseMiddleware):
    def __init__(self, logger: logging.Logger, supported_commands: List[str]):
        self._logger = logger
        self.__supported_commands = supported_commands
        self._logger.info(f"(AnyMiddleware) Supported commands: {self.__supported_commands}")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Any]:
        if isinstance(event, Message):
            command = self.get_command_without_initial_slash(event)

            if command in self.__supported_commands:
                self._logger.info(f"Command '{command}' accessed by user {event.from_user.id}")

            if event.from_user:
                user_id = event.from_user.id

                is_admin_or_moderator = await DatabaseManager.is_admin_or_moderator(user_id)
                if not is_admin_or_moderator and await DatabaseManager.is_command_limited(user_id, settings.MESSAGE_LIMIT, settings.LIMIT_DURATION):
                    await event.answer(get_limit_exceeded_message())
                    return None

        return await handler(event, data)

    @staticmethod
    def get_command_without_initial_slash(event: TelegramObject) -> str:
        return event.text.split()[0][1:]
