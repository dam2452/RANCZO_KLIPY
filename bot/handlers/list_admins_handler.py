import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_no_admins_found_message
from bot.utils.database import DatabaseManager

class ListAdminsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listadmins', 'listad']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/listadmins")
        users = await DatabaseManager.get_admin_users()
        if not users:
            await message.answer(get_no_admins_found_message())
            await self._log_system_message(logging.INFO, "No admins found.")
            return

        response = "📃 Lista adminów:\n"
        response += self._get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Admin list sent to user.")

    def _get_users_string(self, users: List[asyncpg.Record]) -> str:
        return "\n".join([self._format_user(user) for user in users]) + "\n"

    @staticmethod
    def _format_user(user: asyncpg.Record) -> str:
        return f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}"

