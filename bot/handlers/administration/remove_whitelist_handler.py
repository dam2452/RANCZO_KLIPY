import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.remove_whitelist_handler_responses import (
    get_log_user_not_in_whitelist_message,
    get_log_user_removed_message,
    get_no_user_id_provided_message,
    get_user_not_in_whitelist_message,
    get_user_removed_message,
)


class RemoveWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["removewhitelist", "rmw"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_user_id_digit,
            self.__check_user_exists,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_no_user_id_provided_message(),
        )

    async def __check_user_id_digit(self, message: Message) -> bool:
        content = message.text.split()
        if not content[1].isdigit():
            await self._reply_invalid_args_count(message, get_no_user_id_provided_message())
            return False
        return True

    async def __check_user_exists(self, message: Message) -> bool:
        user_id = int(message.text.split()[1])
        user_exists = await DatabaseManager.is_user_in_db(user_id)
        if not user_exists:
            await self._reply_user_not_found(message, user_id)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        user_id = int(message.text.split()[1])

        await DatabaseManager.remove_user(user_id)
        await self.__reply_user_removed(message, user_id)

    async def __reply_user_removed(self, message: Message, user_id: int) -> None:
        await self._answer(message, get_user_removed_message(str(user_id)))
        await self._log_system_message(
            logging.INFO,
            get_log_user_removed_message(str(user_id), message.from_user.username),
        )

    async def _reply_user_not_found(self, message: Message, user_id: int) -> None:
        await self._answer(message, get_user_not_in_whitelist_message(user_id))
        await self._log_system_message(logging.WARNING, get_log_user_not_in_whitelist_message(user_id))
