import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.list_moderators_handler_responses import (
    format_moderators_list,
    get_log_moderators_list_sent_message,
    get_log_no_moderators_found_message,
    get_no_moderators_found_message,
)


class ListModeratorsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["listmoderators", "lm"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        return False

    async def _do_handle(self, message: Message) -> None:
        users = await DatabaseManager.get_moderator_users()
        if not users:
            return await self.__reply_no_moderators_found(message)

        response = format_moderators_list(users)
        await self.__reply_moderators_list(message, response)

    async def __reply_no_moderators_found(self, message: Message) -> None:
        await message.answer(get_no_moderators_found_message())
        await self._log_system_message(logging.INFO, get_log_no_moderators_found_message())

    async def __reply_moderators_list(self, message: Message, response: str) -> None:
        await self._answer_markdown(message , response)
        await self._log_system_message(logging.INFO, get_log_moderators_list_sent_message())
