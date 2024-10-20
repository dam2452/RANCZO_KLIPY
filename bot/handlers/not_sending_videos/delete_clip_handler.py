import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.not_sending_videos.delete_clip_handler_responses import (
    get_clip_deleted_message,
    get_clip_not_exist_message,
    get_invalid_args_count_message,
    get_log_clip_deleted_message,
    get_log_clip_not_exist_message,
)


class DeleteClipHandler(BotMessageHandler):

    def get_commands(self) -> List[str]:
        return ["usunklip", "deleteclip", "uk"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_clip_number_format,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, get_invalid_args_count_message())

    async def __check_clip_number_format(self, message: Message) -> bool:
        content = message.text.split()
        if not content[1].isdigit():
            await self._reply_invalid_args_count(message, get_invalid_args_count_message())
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        clip_number = int(message.text.split()[1])

        user_clips = await DatabaseManager.get_saved_clips(message.chat.id)
        if clip_number not in range(1, len(user_clips) + 1):
            await self._answer(message,get_clip_not_exist_message(clip_number))
            await self._log_system_message(
                logging.INFO,
                get_log_clip_not_exist_message(clip_number, message.from_user.username),
            )
            return

        clip_to_delete = user_clips[clip_number - 1]

        await DatabaseManager.delete_clip(message.chat.id, clip_to_delete.name)

        await self._answer(message,get_clip_deleted_message(clip_to_delete.name))
        await self._log_system_message(
            logging.INFO, get_log_clip_deleted_message(
                clip_to_delete.name,
                message.from_user.username,
            ),
        )
