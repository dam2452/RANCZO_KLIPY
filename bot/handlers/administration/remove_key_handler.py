from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)


class RemoveKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removekey", "rmk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        usage_message = await self.get_response(RK.REMOVE_KEY_USAGE)
        return await self._validate_argument_count(message, 2, usage_message)

    async def _do_handle(self, message: Message) -> None:
        key = message.text.split()[1]
        success = await DatabaseManager.remove_subscription_key(key)
        if success:
            success_message = await self.get_response(RK.REMOVE_KEY_SUCCESS, [key])
            await self._answer(message, success_message)
        else:
            failure_message = await self.get_response(RK.REMOVE_KEY_FAILURE, [key])
            await self._answer(message, failure_message)
