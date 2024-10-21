import logging
from pathlib import Path
import tempfile
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.send_clip_handler_responses import (
    get_clip_not_found_message,
    get_empty_clip_file_message,
    get_empty_file_error_message,
    get_give_clip_name_message,
    get_log_clip_not_found_message,
    get_log_clip_sent_message,
    get_log_empty_clip_file_message,
    get_log_empty_file_error_message,
)


class SendClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["wyślij", "wyslij", "send", "wys"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, get_give_clip_name_message())

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        clip_number = None
        clip_identifier = " ".join(content[1:])

        if clip_identifier.isdigit():
            clip_number = int(clip_identifier)
            clips = await DatabaseManager.get_saved_clips(message.from_user.id)
            if clip_number not in range(1, len(clips)):
                return await self.__reply_clip_not_found(message, clip_number)
            clip = clips[clip_number - 1]
        else:
            clip = await DatabaseManager.get_clip_by_name(message.from_user.id, clip_identifier)

        if not clip:
            return await self.__reply_clip_not_found(message, clip_number)

        if await self._handle_clip_duration_limit_exceeded(message, clip.duration):
            return

        video_data = clip.video_data
        if not video_data:
            return await self.__reply_empty_clip_file(message, clip_identifier)

        temp_file_path = Path(tempfile.gettempdir()) / f"{clip.name}.mp4"

        with temp_file_path.open("wb") as temp_file:
            temp_file.write(video_data)

        if temp_file_path.stat().st_size == 0:
            return await self.__reply_empty_file_error(message, clip_identifier)

        await self._answer_video(message, temp_file_path)

        temp_file_path.unlink()

        await self._log_system_message(logging.INFO, get_log_clip_sent_message(clip.name, message.from_user.username))

    async def __reply_clip_not_found(self, message: Message, clip_number: int) -> None:
        await self._answer(message,get_clip_not_found_message(clip_number))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_not_found_message(clip_number, message.from_user.username),
        )

    async def __reply_empty_clip_file(self, message: Message, clip_name: str) -> None:
        await self._answer(message,get_empty_clip_file_message())
        await self._log_system_message(
            logging.WARNING,
            get_log_empty_clip_file_message(clip_name, message.from_user.username),
        )

    async def __reply_empty_file_error(self, message: Message, clip_name: str) -> None:
        await self._answer(message,get_empty_file_error_message())
        await self._log_system_message(
            logging.ERROR,
            get_log_empty_file_error_message(clip_name, message.from_user.username),
        )
