import logging
import os
import tempfile
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.sending_videos.send_clip_handler_responses import (
    get_clip_not_found_message,
    get_empty_clip_file_message,
    get_empty_file_error_message,
    get_give_clip_name_message,
    get_limit_exceeded_clip_duration_message,
    get_log_clip_not_found_message,
    get_log_clip_sent_message,
    get_log_empty_clip_file_message,
    get_log_empty_file_error_message,
)
from bot.settings import settings
from bot.video.utils import send_video


class SendClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["wyślij", "wyslij", "send", "wys"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        clip_number = None
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_give_clip_name_message())
            return
        clip_identifier = " ".join(content[1:])

        if clip_identifier.isdigit():
            clip_number = int(clip_identifier)
            clips = await DatabaseManager.get_saved_clips(message.from_user.id)
            if clip_number < 1 or clip_number > len(clips):
                return await self.__reply_clip_not_found(message, clip_number)
            clip = clips[clip_number - 1]
        else:
            clip = await DatabaseManager.get_clip_by_name(message.from_user.id, clip_identifier)

        if not clip:
            return await self.__reply_clip_not_found(message, clip_number)

        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and clip.duration > settings.MAX_CLIP_DURATION:
            await message.answer(get_limit_exceeded_clip_duration_message())
            return

        video_data = clip.video_data
        if not video_data:
            return await self.__reply_empty_clip_file(message, clip_identifier)

        temp_file_path = os.path.join(tempfile.gettempdir(), f"{clip.clip_name}.mp4")

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(video_data)

        if os.path.getsize(temp_file_path) == 0:
            return await self.__reply_empty_file_error(message, clip_identifier)

        await send_video(message, temp_file_path, self._bot, self._logger)

        os.remove(temp_file_path)
        await self._log_system_message(logging.INFO, get_log_clip_sent_message(clip.clip_name, message.from_user.username))

    async def __reply_clip_not_found(self, message: Message, clip_number: int) -> None:
        await message.answer(get_clip_not_found_message(clip_number))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_not_found_message(clip_number, message.from_user.username),
        )

    async def __reply_empty_clip_file(self, message: Message, clip_name: str) -> None:
        await message.answer(get_empty_clip_file_message())
        await self._log_system_message(
            logging.WARNING,
            get_log_empty_clip_file_message(clip_name, message.from_user.username),
        )

    async def __reply_empty_file_error(self, message: Message, clip_name: str) -> None:
        await message.answer(get_empty_file_error_message())
        await self._log_system_message(
            logging.ERROR,
            get_log_empty_file_error_message(clip_name, message.from_user.username),
        )
