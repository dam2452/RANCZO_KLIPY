import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.add_whitelist_handler_responses import (
    get_log_user_added_message,
    get_no_username_provided_message,
    get_user_added_message,
)
from bot.utils.functions import parse_whitelist_message


class AddWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["addwhitelist", "addw"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_no_username_provided_message())
            return True
        return False

    async def _do_handle(self, message: Message) -> None:
        user = parse_whitelist_message(message.text.split()[1:])

        await DatabaseManager.add_user(
            user_id=user.user_id,
            username=user.username,
            full_name=user.full_name,
            note=user.note,
            bot=self._bot,
        )

        if not user.username or not user.full_name:
            user_data = await self._bot.get_chat(user.user_id)
            username = user_data.username
            full_name = user_data.full_name
        else:
            username = user.username
            full_name = user.full_name

        await self.__reply_user_added(message, full_name or username)

    async def __reply_user_added(self, message: Message, username: str) -> None:
        await message.answer(get_user_added_message(username))
        await self._log_system_message(logging.INFO, get_log_user_added_message(username, message.from_user.username))
