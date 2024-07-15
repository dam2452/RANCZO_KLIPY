import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.update_whitelist_handler_responses import (
    get_log_user_updated_message,
    get_no_username_provided_message,
    get_user_updated_message,
)
from bot.utils.database import DatabaseManager


class UpdateWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['updatewhitelist', 'updatew']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        username = content[1]
        is_admin = bool(int(content[2])) if len(content) > 2 else None
        is_moderator = bool(int(content[3])) if len(content) > 3 else None
        full_name = content[4] if len(content) > 4 else None
        email = content[5] if len(content) > 5 else None
        phone = content[6] if len(content) > 6 else None

        await DatabaseManager.update_user(username, is_admin, is_moderator, full_name, email, phone)
        await self.__reply_user_updated(message, username)

    async def __reply_user_updated(self, message: Message, username: str) -> None:
        await message.answer(get_user_updated_message(username))
        await self._log_system_message(logging.INFO, get_log_user_updated_message(username, message.from_user.username))
