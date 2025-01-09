import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.update_user_note_handler_responses import (
    get_log_invalid_user_id_message,
    get_log_note_updated_message,
)
from bot.database.response_keys import ResponseKey as RK

class UpdateUserNoteHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["note"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_user_id,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 3, await self.get_response(RK.NO_NOTE_PROVIDED),
        )

    async def __check_user_id(self, message: Message) -> bool:
        user_id_str = message.text.split(maxsplit=2)[1]
        if not user_id_str.isdigit():
            await self.__reply_invalid_user_id(message, user_id_str)
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        note_content = message.text.split(maxsplit=2)
        user_id = int(note_content[1])
        note = note_content[2]

        await self.__update_user_note(message, user_id, note)

    async def __reply_invalid_user_id(self, message: Message, user_id_str: str) -> None:
        await self._answer(message,await self.get_response(RK.INVALID_USER_ID, [user_id_str]))
        await self._log_system_message(logging.INFO, get_log_invalid_user_id_message(message.from_user.username, user_id_str))

    async def __update_user_note(self, message: Message, user_id: int, note: str) -> None:
        await DatabaseManager.update_user_note(user_id, note)
        await self._answer(message,await self.get_response(RK.NOTE_UPDATED))
        await self._log_system_message(logging.INFO, get_log_note_updated_message(message.from_user.username, user_id, note))
