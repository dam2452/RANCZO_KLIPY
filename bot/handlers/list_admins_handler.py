import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_no_admins_found_message
from bot.utils.database import DatabaseManager
from bot.utils.responses import get_users_string


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
        response += get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Admin list sent to user.")
