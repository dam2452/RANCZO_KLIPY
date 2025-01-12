import logging
from pathlib import Path
import tempfile
from typing import (
    List,
    Optional,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.send_clip_handler_responses import (
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
            self.__check_clip_existence,
        ]

    async def __check_clip_existence(self, message: Message) -> bool:
        content = message.text.split()

        clip_identifier = " ".join(content[1:])

        clips = await DatabaseManager.get_saved_clips(message.from_user.id) or []

        if clip_identifier.isdigit():
            clip_number = int(clip_identifier)
            if clip_number < 1 or clip_number > len(clips):
                await self.__reply_clip_not_found(message, clip_number)
                return False
        else:
            clip = await DatabaseManager.get_clip_by_name(message.from_user.id, clip_identifier)
            if not clip:
                await self.__reply_clip_not_found(message, None)
                return False

        return True

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, await self.get_response(RK.GIVE_CLIP_NAME))

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        clip_identifier = " ".join(content[1:])

        if clip_identifier.isdigit():
            clip_number = int(clip_identifier)
            clips = await DatabaseManager.get_saved_clips(message.from_user.id)
            clip = clips[clip_number - 1]
        else:
            clip = await DatabaseManager.get_clip_by_name(message.from_user.id, clip_identifier)

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

        await self._log_system_message(
            logging.INFO,
            get_log_clip_sent_message(clip.name, message.from_user.username),
        )

    async def __reply_clip_not_found(self, message: Message, clip_number: Optional[int]) -> None:
        if clip_number:
            response = await self.get_response(RK.CLIP_NOT_FOUND_NUMBER, [str(clip_number)])
        else:
            response = await self.get_response(RK.CLIP_NOT_FOUND_NAME)
        await self._answer(message, response)
        await self._log_system_message(
            logging.INFO,
            get_log_clip_not_found_message(clip_number, message.from_user.username),
        )

    async def __reply_empty_clip_file(self, message: Message, clip_name: str) -> None:
        await self._answer(message,await self.get_response(RK.EMPTY_CLIP_FILE))
        await self._log_system_message(
            logging.WARNING,
            get_log_empty_clip_file_message(clip_name, message.from_user.username),
        )

    async def __reply_empty_file_error(self, message: Message, clip_name: str) -> None:
        await self._answer(message,await self.get_response(RK.EMPTY_FILE_ERROR))
        await self._log_system_message(
            logging.ERROR,
            get_log_empty_file_error_message(clip_name, message.from_user.username),
        )
