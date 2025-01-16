import json
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
)

from aiogram.types import (
    Message,
    TelegramObject,
)

from bot.middlewares.bot_middleware import BotMiddleware


class AnyMiddleware(BotMiddleware):
    async def handle(
            self,
            handler: Callable[[TelegramObject, json], Awaitable[Any]],
            event: TelegramObject,
            data: json,
    ) -> Optional[Any]:
        if isinstance(event, Message):
            command = self.get_command_without_initial_slash(event)

            if command in self._supported_commands:
                self._logger.info(f"Command '{command}' accessed by user {event.from_user.id}")

        return await handler(event, data)

    @staticmethod
    def get_command_without_initial_slash(event: TelegramObject) -> str:
        return event.text.split()[0][1:]
