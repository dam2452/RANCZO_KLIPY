from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.create_key_handler_responses import (
    get_create_key_success_message,
    get_create_key_usage_message,
)


class CreateKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addkey", "addk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 3, get_create_key_usage_message(),
        )
    async def _do_handle(self, message: Message) -> None:
        args = message.text.split()
        days = int(args[1])
        name = " ".join(args[2:])

        await DatabaseManager.create_subscription_key(days, name)
        await message.answer(get_create_key_success_message(days, name))
