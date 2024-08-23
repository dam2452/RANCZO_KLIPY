import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.administration.update_user_note_handler_responses import (
    get_invalid_user_id_message,
    get_log_invalid_user_id_message,
    get_log_no_note_provided_message,
    get_log_note_updated_message,
    get_no_note_provided_message,
    get_note_updated_message,
)


class UpdateUserNoteHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["note"]

    async def _do_handle(self, message: Message) -> None:
        note_content = message.text.split(maxsplit=2)
        if len(note_content) < 3:
            return await self.__reply_no_note_provided(message)

        user_id_str, note = note_content[1], note_content[2]

        try:
            user_id = int(user_id_str)
        except ValueError:
            return await self.__reply_invalid_user_id(message, user_id_str)

        await self.__update_user_note(message, user_id, note)

    async def __reply_no_note_provided(self, message: Message) -> None:
        await message.answer(get_no_note_provided_message())
        await self._log_system_message(logging.INFO, get_log_no_note_provided_message(message.from_user.username))

    async def __reply_invalid_user_id(self, message: Message, user_id_str: str) -> None:
        await message.answer(get_invalid_user_id_message(user_id_str))
        await self._log_system_message(logging.INFO, get_log_invalid_user_id_message(message.from_user.username, user_id_str))

    async def __update_user_note(self, message: Message, user_id: int, note: str) -> None:
        await DatabaseManager.update_user_note(user_id, note)
        await message.answer(get_note_updated_message())
        await self._log_system_message(logging.INFO, get_log_note_updated_message(message.from_user.username, user_id, note))
