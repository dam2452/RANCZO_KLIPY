import logging
from typing import List

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
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username or days provided for adding subscription.")
            return

        username = content[1]
        days = int(content[2])

        new_end_date = await DatabaseManager.add_subscription(username, days)
        await message.answer(get_subscription_extended_message(username, new_end_date))
        await self._log_system_message(logging.INFO,
                                       f"Subscription for user {username} extended by {message.from_user.username}.")
