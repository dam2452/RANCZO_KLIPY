import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import (
    get_no_username_provided_message,
    get_subscription_removed_message
)
from bot.utils.database import DatabaseManager


class RemoveSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['removesubscription', 'removesub']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/removesubscription {message.text}")
        content = message.text.split()
        if len(content) < 2:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for removing subscription.")
            return

        username = content[1]

        await DatabaseManager.remove_subscription(username)
        await message.answer(get_subscription_removed_message(username))
        await self._log_system_message(logging.INFO,
                                       f"Subscription for user {username} removed by {message.from_user.username}.")
