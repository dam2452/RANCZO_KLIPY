import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.utils.database import DatabaseManager
from bot.utils.responses import (
    get_no_username_provided_message,
    get_user_added_message,
)


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['addwhitelist', 'addw']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/addwhitelist {message.text}")
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_username_provided_message())

        # fixme jakos ogarnac duplikat
        username = content[1]
        is_admin = bool(int(content[2])) if len(content) > 2 else False
        is_moderator = bool(int(content[3])) if len(content) > 3 else False
        full_name = content[4] if len(content) > 4 else None
        email = content[5] if len(content) > 5 else None
        phone = content[6] if len(content) > 6 else None

        await DatabaseManager.add_user(username, is_admin, is_moderator, full_name, email, phone)
        await self.__reply_user_added(message, username)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await message.answer(get_user_added_message(username))
        await self._log_system_message(logging.INFO, f"User {username} added to whitelist by {message.from_user.username}.")
