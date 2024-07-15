from datetime import date
import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.add_subscription_handler_responses import (
    get_no_username_provided_message,
    get_subscription_error_log_message,
    get_subscription_error_message,
    get_subscription_extended_message,
    get_subscription_log_message,
)
from bot.utils.database_manager import DatabaseManager


class AddSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['addsubscription', 'addsub']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 3:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        username = content[1]
        days = int(content[2])

        new_end_date = await DatabaseManager.add_subscription(username, days)
        if new_end_date is None:
            return await self.__reply_subscription_error(message)

        await self.__reply_subscription_extended(message, username, new_end_date)

    async def __reply_subscription_extended(self, message: Message, username: str, new_end_date: date) -> None:
        await message.answer(get_subscription_extended_message(username, new_end_date))
        await self._log_system_message(logging.INFO, get_subscription_log_message(username, message.from_user.username))

    async def __reply_subscription_error(self, message: Message) -> None:
        await message.answer(get_subscription_error_message())
        await self._log_system_message(logging.ERROR, get_subscription_error_log_message())
