from datetime import date
import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.add_subscription_handler_responses import (
    get_no_user_id_provided_message,
    get_subscription_error_log_message,
    get_subscription_error_message,
    get_subscription_extended_message,
    get_subscription_log_message,
)


class AddSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addsubscription", "addsub"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 3 or not content[1].isdigit() or not content[2].isdigit():
            await self._reply_invalid_args_count(message, get_no_user_id_provided_message())
            return True
        return False

    async def _do_handle(self, message: Message) -> None:
        user_id = int(message.text.split()[1])
        days = int(message.text.split()[2])

        new_end_date = await DatabaseManager.add_subscription(user_id, days)
        if new_end_date is None:
            return await self.__reply_subscription_error(message)

        await self.__reply_subscription_extended(message, user_id, new_end_date)

    async def __reply_subscription_extended(self, message: Message, user_id: int, new_end_date: date) -> None:
        await message.answer(get_subscription_extended_message(str(user_id), new_end_date))
        await self._log_system_message(logging.INFO, get_subscription_log_message(str(user_id), message.from_user.username))

    async def __reply_subscription_error(self, message: Message) -> None:
        await message.answer(get_subscription_error_message())
        await self._log_system_message(logging.ERROR, get_subscription_error_log_message())
