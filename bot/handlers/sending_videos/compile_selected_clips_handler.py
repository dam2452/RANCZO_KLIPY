import logging
import tempfile
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.sending_videos.compile_selected_clips_handler_responses import (
    get_clip_time_message,
    get_compiled_clip_sent_message,
    get_invalid_args_count_message,
    get_log_no_matching_clips_found_message,
    get_max_clips_exceeded_message,
    get_no_matching_clips_found_message,
)
from bot.settings import settings
from bot.video.clips_compiler import (
    ClipsCompiler,
    process_compiled_clip,
)


class CompileSelectedClipsHandler(BotMessageHandler):
    class ClipNotFoundException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ["połączklipy", "polaczklipy", "concatclips", "pk"]

    async def is_any_validation_failed(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_invalid_args_count_message())
            return True
        return False

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        try:
            clip_numbers = [int(clip) for clip in content[1:]]
        except ValueError:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        user_clips = await DatabaseManager.get_saved_clips(message.from_user.id)

        selected_clips = []
        for clip_number in clip_numbers:
            if 1 <= clip_number <= len(user_clips):
                selected_clips.append(user_clips[clip_number - 1])
            else:
                return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        if not selected_clips:
            return await self.__reply_no_matching_clips_found(message)

        selected_segments = []
        for clip in selected_clips:
            temp_file = tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4")
            temp_file.write(clip.video_data)
            temp_file.close()
            selected_segments.append({
                "video_path": temp_file.name,
                "start": 0,
                "end": clip.duration,
            })

        total_duration = sum(clip.duration for clip in selected_clips)
        is_admin_or_moderator = await DatabaseManager.is_admin_or_moderator(message.from_user.id)

        if not is_admin_or_moderator:
            if total_duration > settings.MAX_CLIP_DURATION:
                await message.answer(get_clip_time_message())
                return
            if len(selected_segments) > settings.MAX_CLIPS_PER_COMPILATION:
                await message.answer(get_max_clips_exceeded_message())
                return

        compiled_output = await ClipsCompiler.compile_and_send_clips(message, selected_segments, self._bot, self._logger)
        await process_compiled_clip(message, compiled_output, ClipType.COMPILED)

        await self._log_system_message(logging.INFO, get_compiled_clip_sent_message(message.from_user.username))

    async def __reply_no_matching_clips_found(self, message: Message) -> None:
        await message.answer(get_no_matching_clips_found_message())
        await self._log_system_message(logging.INFO, get_log_no_matching_clips_found_message())
