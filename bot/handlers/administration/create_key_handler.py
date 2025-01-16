import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.create_key_handler_responses import (
    get_key_added_message,
    get_log_key_name_exists_message,
    get_wrong_argument_message,
)


class CreateKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addkey", "addk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_days_is_digit,
            self.__check_key_is_unique,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 3, await self.get_response(RK.CREATE_KEY_USAGE),
        )

    async def __check_days_is_digit(self, message: Message) -> bool:
        args = message.text.split()
        if not args[1].isdigit():
            await self.__reply_wrong_argument(message)
            return False
        return True

    async def __check_key_is_unique(self, message: Message) -> bool:
        args = message.text.split()
        key = " ".join(args[2:])
        key_exists = await DatabaseManager.get_subscription_days_by_key(key)
        if key_exists is not None:
            await self.__reply_key_already_exists(message, key)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        args = message.text.split()
        days = int(args[1])
        key = " ".join(args[2:])

        await DatabaseManager.create_subscription_key(days, key)
        await self.__reply_key_added(message, days, key)

    async def __reply_key_added(self, message: Message, days: int, key: str) -> None:
        await self._answer(message, await self.get_response(RK.CREATE_KEY_SUCCESS, [key, days]))
        await self._log_system_message(
            logging.INFO, get_key_added_message(key, days),
        )

    async def __reply_wrong_argument(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.CREATE_KEY_USAGE))
        await self._log_system_message(logging.INFO, get_wrong_argument_message())

    async def __reply_key_already_exists(self, message: Message, key: str) -> None:
        await self._answer(message, await self.get_response(RK.KEY_ALREADY_EXISTS, [key]))
        await self._log_system_message(logging.INFO, get_log_key_name_exists_message(key))
