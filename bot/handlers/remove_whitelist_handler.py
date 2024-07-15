import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.remove_whitelist_handler_responses import (
    get_log_user_removed_message,
    get_no_username_provided_message,
    get_user_removed_message,
)
from bot.utils.database_manager import DatabaseManager


class RemoveWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['removewhitelist', 'removew']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        username = content[1]
        await DatabaseManager.remove_user(username)
        await self.__reply_user_removed(message, username)

    async def __reply_user_removed(self, message: Message, username: str) -> None:
        await message.answer(get_user_removed_message(username))
        await self._log_system_message(logging.INFO, get_log_user_removed_message(username, message.from_user.username))
