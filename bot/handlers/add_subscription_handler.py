import logging
from typing import List
from datetime import date

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import (
    get_no_username_provided_message,
    get_subscription_extended_message
)
from bot.utils.database import DatabaseManager


class AddSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['addsubscription', 'addsub']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/addsubscription {message.text}")
        content = message.text.split()

        if len(content) < 3:
            return await self.__reply_no_username_or_days_provided(message)

        username = content[1]
        days = int(content[2])

        new_end_date: date | None = await DatabaseManager.add_subscription(username, days)
        if new_end_date is None:
            return await self.__reply_subscription_error(message)

        await self.__reply_subscription_extended(message, username, new_end_date)

    async def __reply_no_username_or_days_provided(self, message: Message) -> None:
        await message.answer(get_no_username_provided_message())
        await self._log_system_message(logging.INFO, "No username or days provided for adding subscription.")

    async def __reply_subscription_extended(self, message: Message, username: str, new_end_date: date) -> None:
        await message.answer(get_subscription_extended_message(username, new_end_date))
        await self._log_system_message(logging.INFO, f"Subscription for user {username} extended by {message.from_user.username}.")

    async def __reply_subscription_error(self, message: Message) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas przedłużania subskrypcji.⚠️")
        await self._log_system_message(logging.ERROR, "An error occurred while extending the subscription.")
