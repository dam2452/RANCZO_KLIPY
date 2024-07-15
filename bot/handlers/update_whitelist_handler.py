import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.update_whitelist_handler_responses import (
    get_log_user_updated_message,
    get_no_username_provided_message,
    get_user_updated_message,
)
from bot.utils.database_manager import DatabaseManager
from bot.utils.functions import parse_whitelist_message


class UpdateWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['updatewhitelist', 'updatew']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        user = parse_whitelist_message(content, default_admin_status=None, default_moderator_status=None)
        await DatabaseManager.update_user(user)
        await self.__reply_user_updated(message, user.name)

    async def __reply_user_updated(self, message: Message, username: str) -> None:
        await message.answer(get_user_updated_message(username))
        await self._log_system_message(logging.INFO, get_log_user_updated_message(username, message.from_user.username))
