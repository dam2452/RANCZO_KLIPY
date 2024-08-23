import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.list_user_keys_handler_responses import (
    create_user_keys_response,
    get_log_user_keys_empty_message,
    get_log_user_keys_sent_message,
    get_user_keys_empty_message,
)


class ListUserMessagesHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["listkey", "lk"]

    async def _do_handle(self, message: Message) -> None:
        messages = await DatabaseManager.get_all_user_keys()
        if not messages:
            return await self.__reply_user_keys_empty(message)

        response = create_user_keys_response(messages)
        await self.__reply_user_keys(message, response)

    async def __reply_user_keys_empty(self, message: Message) -> None:
        await message.answer(get_user_keys_empty_message())
        await self._log_system_message(logging.INFO, get_log_user_keys_empty_message())

    async def __reply_user_keys(self, message: Message, response: str) -> None:
        await message.answer(response, parse_mode="Markdown")
        await self._log_system_message(logging.INFO, get_log_user_keys_sent_message())
