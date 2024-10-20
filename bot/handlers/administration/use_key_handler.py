import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.use_key_handler_responses import (
    get_invalid_key_message,
    get_log_message_saved,
    get_no_message_provided_message,
    get_subscription_redeemed_message,
)


class SaveUserKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["klucz", "key"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_no_message_provided_message(),
        )

    async def _do_handle(self, message: Message) -> None:
        key = message.text.split(maxsplit=1)[1]

        subscription_days = await DatabaseManager.get_subscription_days_by_key(key)
        if subscription_days:
            await DatabaseManager.add_user(
                message.from_user.id, message.from_user.username, message.from_user.full_name,
                None, self._bot,
            )
            await DatabaseManager.add_subscription(message.from_user.id, subscription_days)
            await DatabaseManager.remove_subscription_key(key)
            await self._answer(message,get_subscription_redeemed_message(subscription_days))
        else:
            await self._answer(message,get_invalid_key_message())

        await self._log_system_message(logging.INFO, get_log_message_saved(message.from_user.id))
