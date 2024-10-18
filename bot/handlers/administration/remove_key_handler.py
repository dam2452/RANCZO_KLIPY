from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.remove_key_handler_responses import (
    get_remove_key_failure_message,
    get_remove_key_success_message,
    get_remove_key_usage_message,
)


class RemoveKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removekey", "rmk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_remove_key_usage_message(),
        )

    async def _do_handle(self, message: Message) -> None:
        key = message.text.split()[1]
        success = await DatabaseManager.remove_subscription_key(key)
        if success:
            await message.answer(get_remove_key_success_message(key))
        else:
            await message.answer(get_remove_key_failure_message(key))
