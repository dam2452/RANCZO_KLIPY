import logging
import asyncpg
from typing import List
from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_no_moderators_found_message
from bot.utils.database import DatabaseManager


class ListModeratorsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listmoderators', 'listmod']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/listmoderators")
        users = await DatabaseManager.get_moderator_users()
        if not users:
            await message.answer(get_no_moderators_found_message())
            await self._log_system_message(logging.INFO, "No moderators found.")
            return

        response = "📃 Lista moderatorów 📃\n"
        response += self.__get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Moderator list sent to user.")

    def __get_users_string(self, users: List[asyncpg.Record]) -> str:
        return "\n".join([self.__format_user(user) for user in users]) + "\n"

    @staticmethod
    def __format_user(user: asyncpg.Record) -> str:
        return (f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 "
                f"Phone: {user['phone']}")
