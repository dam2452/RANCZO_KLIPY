import logging

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Awaitable

from bot.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data) -> Awaitable: # TO DO: Change return type
        try:
            return await handler(event, data)
        except Exception as e:
            message = event if isinstance(event, Message) else None
            if message:
                await message.answer("⚠️ Wystąpił błąd podczas przetwarzania Twojego żądania. Prosimy spróbować ponownie później.⚠️")
                await DatabaseManager.log_system_message("ERROR", f"Error processing request from user '{message.from_user.username}': {e}")

            error_message = f"An error occurred: {e}"
            logger.error(error_message, exc_info=True)
            await DatabaseManager.log_system_message("ERROR", error_message)
