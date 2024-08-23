import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.save_user_info_handler_responses import (
    get_log_message_saved,
    get_message_saved_confirmation,
    get_no_message_provided_message,
)


class SaveUserKeyHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["klucz", "key"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split(maxsplit=1)
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_no_message_provided_message())
            return

        message_content = content[1]

        await DatabaseManager.save_user_message(message.from_user.id, message_content)
        await message.answer(get_message_saved_confirmation())
        await self._log_system_message(logging.INFO, get_log_message_saved(message.from_user.id))
