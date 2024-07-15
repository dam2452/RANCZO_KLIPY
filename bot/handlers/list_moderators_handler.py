import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.utils.database import DatabaseManager
from bot.handlers.responses.list_moderators_handler_responses import (
    get_no_moderators_found_message,
    get_users_string,
    get_log_no_moderators_found_message,
    get_log_moderators_list_sent_message
)


class ListModeratorsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listmoderators', 'listmod']

    async def _do_handle(self, message: Message) -> None:
        command = self.get_commands()[0]
        await self._log_user_activity(message.from_user.username, f"/{command}")
        users = await DatabaseManager.get_moderator_users()
        if not users:
            return await self.__reply_no_moderators_found(message)

        response = "📃 Lista moderatorów:\n"
        response += get_users_string(users)
        await self.__reply_moderators_list(message, response)

    async def __reply_no_moderators_found(self, message: Message) -> None:
        await message.answer(get_no_moderators_found_message())
        await self._log_system_message(logging.INFO, get_log_no_moderators_found_message())

    async def __reply_moderators_list(self, message: Message, response: str) -> None:
        await message.answer(response)
        await self._log_system_message(logging.INFO, get_log_moderators_list_sent_message())
