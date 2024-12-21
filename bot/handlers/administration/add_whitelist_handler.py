import logging
from typing import List

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.add_whitelist_handler_responses import (
    get_log_user_added_message,
    get_no_username_provided_message,
    get_user_added_message,
    get_user_not_found_message,
)


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addwhitelist", "addw"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, get_no_username_provided_message(),
        )

    async def _do_handle(self, message: Message) -> None:
        user_input = message.text.split()[1]
        try:
            user_data = await self._bot.get_chat(int(user_input) if user_input.isdigit() else user_input)
        except TelegramBadRequest as e:
            if "chat not found" in str(e).lower():
                await self._answer(message, get_user_not_found_message())
                return
            raise

        await DatabaseManager.add_user(
            user_id=user_data.id,
            username=user_data.username,
            full_name=user_data.full_name,
            note=None,
        )

        username_or_name = user_data.username or user_data.full_name or str(user_data.id)
        await self.__reply_user_added(message, username_or_name)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await self._answer(message,get_user_added_message(username))
        await self._log_system_message(logging.INFO, get_log_user_added_message(username, message.from_user.username))
