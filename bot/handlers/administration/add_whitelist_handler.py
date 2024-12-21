import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.add_whitelist_handler_responses import (
    get_log_user_added_message,
    get_no_user_id_provided_message,
    get_no_username_provided_message,
    get_user_added_message,
)


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addwhitelist", "addw"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_user_id_is_digit,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_no_username_provided_message(),
        )

    async def __check_user_id_is_digit(self, message: Message) -> bool:
        user_input = message.text.split()[1]
        if not user_input.isdigit():
            await self.__reply_user_not_found(message)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        user_input = message.text.split()[1]

        await DatabaseManager.add_user(
            user_id=int(user_input),
            username="",
            full_name="",
            note=None,
        )
        await self.__reply_user_added(message, user_input)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await self._answer(message, get_user_added_message(username))
        await self._log_system_message(
            logging.INFO,
            get_log_user_added_message(username, message.from_user.username),
        )

    async def __reply_user_not_found(self, message: Message) -> None:
        await self._answer(message, get_no_user_id_provided_message())
        await self._log_system_message(logging.INFO, get_no_user_id_provided_message())
