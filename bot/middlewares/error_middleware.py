import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
)

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
            self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
            data: Dict[str, Any],
    ) -> Optional[Awaitable]:
        return await handler(event, data)
