import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.add_whitelist_handler_responses import (
    get_log_user_added_message,
    get_no_username_provided_message,
    get_user_added_message,
)
from bot.utils.database import DatabaseManager
from bot.utils.functions import parse_whitelist_message


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['addwhitelist', 'addw']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        user = parse_whitelist_message(content, default_admin_status=False, default_moderator_status=False)
        await DatabaseManager.add_user(user)
        await self.__reply_user_added(message, user.name)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await message.answer(get_user_added_message(username))
        await self._log_system_message(logging.INFO, get_log_user_added_message(username, message.from_user.username))
