import logging

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            message = event if isinstance(event, Message) else None
            if message:
                await message.answer(
                    "⚠️ Wystąpił błąd podczas przetwarzania Twojego żądania. Prosimy spróbować ponownie później.⚠️")
            logger.error(f"An error occurred: {e}", exc_info=True)
