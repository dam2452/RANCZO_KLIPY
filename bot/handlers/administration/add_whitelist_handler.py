import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.add_whitelist_handler_responses import (
    get_log_user_added_message,
    get_no_username_provided_message,
    get_user_added_message,
)
from bot.utils.functions import parse_whitelist_message


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['addwhitelist', 'addw']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        user = parse_whitelist_message(content)

        await DatabaseManager.add_user(user, bot=self._bot)

        await self.__reply_user_added(message, user.full_name or user.username)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await message.answer(get_user_added_message(username))
        await self._log_system_message(logging.INFO, get_log_user_added_message(username, message.from_user.username))
