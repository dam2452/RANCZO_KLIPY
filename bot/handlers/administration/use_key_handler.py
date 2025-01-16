import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.use_key_handler_responses import get_log_message_saved


class SaveUserKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["klucz", "key"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, await self.get_response(RK.NO_KEY_PROVIDED),
        )

    async def _do_handle(self, message: Message) -> None:
        key = message.text.split(maxsplit=1)[1]

        subscription_days = await DatabaseManager.get_subscription_days_by_key(key)
        if subscription_days:
            await DatabaseManager.add_user(
                message.from_user.id, message.from_user.username, message.from_user.full_name,
                None,
            )
            await DatabaseManager.add_subscription(message.from_user.id, subscription_days)
            await DatabaseManager.remove_subscription_key(key)
            await self._answer(
                message,await self.get_response(RK.SUBSCRIPTION_REDEEMED, [str(subscription_days)]),
)
        else:
            await self._answer(
                message,await self.get_response(RK.INVALID_KEY),
)

        await self._log_system_message(logging.INFO, get_log_message_saved(message.from_user.id))
