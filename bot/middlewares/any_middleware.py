import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    List,
)

from aiogram import BaseMiddleware
from aiogram.types import (
    Message,
    TelegramObject,
)


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
    ) -> Optional[Awaitable]:
        if not isinstance(event, Message):
            return await handler(event, data)

        command = self.get_command_without_initial_slash(event)
        if command in self.__supported_commands:
            self._logger.info(f"Command '{command}' accessed by user {event.from_user.id}")
            return await handler(event, data)

        return await handler(event, data)

    @staticmethod
    def get_command_without_initial_slash(event: TelegramObject) -> str:
        return event.text.split()[0][1:]

