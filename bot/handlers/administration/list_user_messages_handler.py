import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.list_user_messages_handler_responses import (
    create_user_messages_response,
    get_log_user_messages_empty_message,
    get_log_user_messages_sent_message,
    get_user_messages_empty_message,
)


class ListUserMessagesHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listusermessages', 'listmsg']

    async def _do_handle(self, message: Message) -> None:
        messages = await DatabaseManager.get_all_user_messages()
        if not messages:
            return await self.__reply_user_messages_empty(message)

        response = create_user_messages_response(messages)
        await self.__reply_user_messages(message, response)

    async def __reply_user_messages_empty(self, message: Message) -> None:
        await message.answer(get_user_messages_empty_message())
        await self._log_system_message(logging.INFO, get_log_user_messages_empty_message())

    async def __reply_user_messages(self, message: Message, response: str) -> None:
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, get_log_user_messages_sent_message())
