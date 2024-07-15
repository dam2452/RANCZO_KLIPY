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

        return self.handle(handler, event, data)

    @abstractmethod
    async def handle(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        pass
