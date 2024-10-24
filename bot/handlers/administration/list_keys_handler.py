import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.list_keys_handler_responses import (
    create_subscription_keys_response,
    get_log_subscription_keys_empty_message,
    get_log_subscription_keys_sent_message,
    get_subscription_keys_empty_message,
)


class ListKeysHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["listkey", "lk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return []

    async def _do_handle(self, message: Message) -> None:
        keys = await DatabaseManager.get_all_subscription_keys()
        if not keys:
            return await self.__reply_subscription_keys_empty(message)

        response = create_subscription_keys_response(keys)
        await self.__reply_subscription_keys(message, response)

    async def __reply_subscription_keys_empty(self, message: Message) -> None:
        await self._answer(message,get_subscription_keys_empty_message())
        await self._log_system_message(logging.INFO, get_log_subscription_keys_empty_message())

    async def __reply_subscription_keys(self, message: Message, response: str) -> None:
        await self._answer_markdown(message , response)
        await self._log_system_message(logging.INFO, get_log_subscription_keys_sent_message())
