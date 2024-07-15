import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.list_admins_handler_responses import (
    get_log_admins_list_sent_message,
    get_log_no_admins_found_message,
    get_no_admins_found_message,
    get_users_string,
)
from bot.utils.database import DatabaseManager


class ListAdminsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listadmins', 'listad']

    async def _do_handle(self, message: Message) -> None:
        command = self.get_commands()[0]
        await self._log_user_activity(message.from_user.username, f"/{command}")
        users = await DatabaseManager.get_admin_users()
        if not users:
            return await self.__reply_no_admins_found(message)

        response = "📃 Lista adminów:\n"
        response += get_users_string(users)

        await self.__reply_admins_list(message, response)

    async def __reply_no_admins_found(self, message: Message) -> None:
        await message.answer(get_no_admins_found_message())
        await self._log_system_message(logging.INFO, get_log_no_admins_found_message())

    async def __reply_admins_list(self, message: Message, response: str) -> None:
        await message.answer(response)
        await self._log_system_message(logging.INFO, get_log_admins_list_sent_message())
