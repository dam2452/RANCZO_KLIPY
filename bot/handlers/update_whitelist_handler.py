import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import (
    get_no_username_provided_message,
    get_user_updated_message
)
from bot.utils.database import DatabaseManager


class UpdateWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['updatewhitelist', 'updatew']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/updatewhitelist {message.text}")
        content = message.text.split()
        if len(content) < 2:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for updating whitelist.")
            return

        username = content[1]
        is_admin = bool(int(content[2])) if len(content) > 2 else None
        is_moderator = bool(int(content[3])) if len(content) > 3 else None
        full_name = content[4] if len(content) > 4 else None
        email = content[5] if len(content) > 5 else None
        phone = content[6] if len(content) > 6 else None

        await DatabaseManager.update_user(username, is_admin, is_moderator, full_name, email, phone)
        await message.answer(get_user_updated_message(username))
        await self._log_system_message(logging.INFO, f"User {username} updated by {message.from_user.username}.")
