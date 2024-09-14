
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
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
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Any]:
        if isinstance(event, Message):
            command = self.get_command_without_initial_slash(event)

            if command in self.__supported_commands:
                self._logger.info(f"Command '{command}' accessed by user {event.from_user.id}")

        return await handler(event, data)

    @staticmethod
    def get_command_without_initial_slash(event: TelegramObject) -> str:
        return event.text.split()[0][1:]
