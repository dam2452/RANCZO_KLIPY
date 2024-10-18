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
    get_no_username_provided_message,
    get_subscription_removed_message,
)
from bot.utils.functions import validate_argument_count


class RemoveSubscriptionHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removesubscription", "rmsub"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self._validate_argument_count,
        ]

    async def _validate_argument_count(self, message: Message) -> bool:
        return await validate_argument_count(
            message, 2, self._reply_invalid_args_count,
            get_no_username_provided_message(),
        )

    async def _do_handle(self, message: Message) -> None:
        username = message.text.split()[1]
        await DatabaseManager.remove_subscription(message.from_user.id)
        await self.__reply_subscription_removed(message, username)

    async def __reply_subscription_removed(self, message: Message, username: str) -> None:
        await message.answer(get_subscription_removed_message(username))
        await self._log_system_message(logging.INFO, get_log_subscription_removed_message(username, message.from_user.username))
