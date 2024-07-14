import logging
from typing import List

from aiogram.types import Message

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_no_moderators_found_message, get_users_string
from bot.utils.database import DatabaseManager


class ListModeratorsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listmoderators', 'listmod']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/listmoderators")
        users = await DatabaseManager.get_moderator_users()
        if not users:
            return await self.__reply_no_moderators_found(message)

        response = "📃 Lista moderatorów:\n"
        response += get_users_string(users)
        await self.__reply_moderators_list(message, response)

    async def __reply_no_moderators_found(self, message: Message) -> None:
        await message.answer(get_no_moderators_found_message())
        await self._log_system_message(logging.INFO, "No moderators found.")

    async def __reply_moderators_list(self, message: Message, response: str) -> None:
        await message.answer(response)
        await self._log_system_message(logging.INFO, "Moderator list sent to user.")
