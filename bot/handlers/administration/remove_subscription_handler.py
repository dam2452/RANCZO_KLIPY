import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.remove_subscription_handler_responses import (
    get_log_subscription_removed_message,
    get_no_user_id_provided_message,
    get_subscription_removed_message,
)


class RemoveSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removesubscription", "rmsub"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_user_id_is_digit,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_no_user_id_provided_message(),
        )

    async def __check_user_id_is_digit(self, message: Message) -> bool:
        user_input = message.text.split()[1]
        if not user_input.isdigit():
            await self.__reply_invalid_user_id(message)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        user_id = int(message.text.split()[1])

        await DatabaseManager.remove_subscription(user_id)
        await self.__reply_subscription_removed(message, user_id)

    async def __reply_subscription_removed(self, message: Message, user_id: int) -> None:
        await self._answer(message, get_subscription_removed_message(str(user_id)))
        await self._log_system_message(
            logging.INFO,
            get_log_subscription_removed_message(str(user_id), message.from_user.username),
        )

    async def __reply_invalid_user_id(self, message: Message) -> None:
        await self._answer(message, get_no_user_id_provided_message())
        await self._log_system_message(logging.WARNING, get_no_user_id_provided_message())
