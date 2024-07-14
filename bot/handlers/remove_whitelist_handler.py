import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.utils.database import DatabaseManager
from bot.utils.responses import (
    get_no_username_provided_message,
    get_user_removed_message,
)


class RemoveWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['removewhitelist', 'removew']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/removewhitelist {message.text}")
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        username = content[1]
        await DatabaseManager.remove_user(username)
        await self.__reply_user_removed(message, username)

    async def __reply_user_removed(self, message: Message, username: str) -> None:
        await message.answer(get_user_removed_message(username))
        await self._log_system_message(logging.INFO, f"User {username} removed from whitelist by {message.from_user.username}.")
