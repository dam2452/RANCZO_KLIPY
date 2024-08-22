from datetime import datetime
import logging
import tempfile
from typing import (
    List,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    ClipType,
    LastClip,
)
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.sending_videos.compile_selected_clips_handler_responses import (
    get_clip_not_found_message,
    get_compiled_clip_sent_message,
    get_invalid_args_count_message,
    get_log_clip_not_found_message,
    get_log_no_matching_clips_found_message,
    get_no_matching_clips_found_message,
)
from bot.video.clips_compiler import ClipsCompiler


class CompileSelectedClipsHandler(BotMessageHandler):
    class ClipNotFoundException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ['polaczklipy', 'concatclips', 'pk']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        clip_names = content[1:]
        selected_clips_data = await self.__get_selected_clips_data(clip_names, message.from_user.username, message)

        if not selected_clips_data:
            return await self.__reply_no_matching_clips_found(message)

        selected_segments = []
        for clip_data, duration in selected_clips_data:
            temp_file = tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4")
            temp_file.write(clip_data)
            temp_file.close()
            selected_segments.append({
                'video_path': temp_file.name,
                'start': 0,
                'end': duration,
            })

        compiled_output = await ClipsCompiler.compile_and_send_clips(message, selected_segments, self._bot, self._logger)
        with open(compiled_output, 'rb') as f:
            compiled_clip_data = f.read()

        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment={},
            compiled_clip=compiled_clip_data,
            clip_type=ClipType.COMPILED.value,
            adjusted_start_time=None,
            adjusted_end_time=None,
            is_adjusted=False,
        )

        await self._log_system_message(logging.INFO, get_compiled_clip_sent_message(message.from_user.username))

    async def __get_selected_clips_data(self, clip_names: List[str], username: str, message: Message) -> List[Tuple[bytes, int]]:
        selected_clips_data = []
        for clip_name in clip_names:
            clip = await DatabaseManager.get_clip_by_name(message.from_user.id, clip_name)
            if not clip:
                await self.__reply_clip_not_found(message, clip_name, username)
            else:
                selected_clips_data.append((clip.video_data, clip.duration))
        return selected_clips_data

    async def __reply_clip_not_found(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_not_found_message(clip_name))
        await self._log_system_message(logging.INFO, get_log_clip_not_found_message(clip_name, username))

    async def __reply_no_matching_clips_found(self, message: Message) -> None:
        await message.answer(get_no_matching_clips_found_message())
        await self._log_system_message(logging.INFO, get_log_no_matching_clips_found_message())
