import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.list_whitelist_handler_responses import (
    create_whitelist_response,
    get_log_whitelist_empty_message,
    get_log_whitelist_sent_message,
    get_whitelist_empty_message,
)


class ListWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["listwhitelist", "lw"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        users = await DatabaseManager.get_all_users()
        if not users:
            return await self.__reply_whitelist_empty(message)

        response = create_whitelist_response(users)
        await self.__reply_whitelist(message, response)

    async def __reply_whitelist_empty(self, message: Message) -> None:
        await self._answer(message,get_whitelist_empty_message())
        await self._log_system_message(logging.INFO, get_log_whitelist_empty_message())

    async def __reply_whitelist(self, message: Message, response: str) -> None:
        await self._answer_markdown(message , response)
        await self._log_system_message(logging.INFO, get_log_whitelist_sent_message())
