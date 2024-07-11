import logging
import tempfile
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.clip_handler import last_selected_segment
from bot.handlers.search_handler import last_search_quotes
from bot.settings import Settings
from bot.utils.video_handler import (
    FFmpegException,
    VideoManager,
    VideoProcessor,
)


class AdjustVideoClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['dostosuj', 'adjust', 'd']

    def get_action_name(self) -> str:
        return "adjust_video_clip"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/dostosuj {message.text}")
        content = message.text.split()

        if len(content) == 4:
            if message.chat.id not in last_search_quotes:
                return await self.__reply_no_previous_searches(message)
            index = int(content[1]) - 1
            segments = last_search_quotes[message.chat.id]
            segment_info = segments[index]
        elif len(content) == 3:
            if message.chat.id not in last_selected_segment:
                return await self.__reply_no_quotes_selected(message)
            segment_info = last_selected_segment[message.chat.id]
        else:
            return await self.__reply_invalid_args_count(message)

        await self._log_system_message(logging.INFO, f"Segment Info: {segment_info}")

        original_start_time = segment_info['start'] - Settings.EXTEND_BEFORE
        original_end_time = segment_info['end'] + Settings.EXTEND_AFTER

        additional_start_offset = float(content[-2])
        additional_end_offset = float(content[-1])

        start_time = max(0, original_start_time - additional_start_offset)
        end_time = original_end_time + additional_end_offset

        if end_time <= start_time:
            return await self.__reply_invalid_interval(message)

        with tempfile.NamedTemporaryFile(suffix=".mp4") as output_file:
            try:
                await VideoProcessor.extract_clip(segment_info['video_path'], start_time, end_time, output_file.name)
            except FFmpegException as e:
                return await self.__reply_extraction_failure(message, e)

            await VideoManager(self._bot).send_video(message.chat.id, output_file.name)

        segment_info['start'] = start_time
        segment_info['end'] = end_time
        last_selected_segment[message.chat.id] = segment_info
        await self._log_system_message(logging.INFO, f"Updated segment info for chat ID '{message.chat.id}'")
        await self._log_system_message(logging.INFO, f"Video clip adjusted successfully for user '{message.from_user.username}'.")

    async def __reply_no_previous_searches(self, message: Message) -> None:
        await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_no_quotes_selected(self, message: Message) -> None:
        await message.answer("⚠️ Najpierw wybierz cytat za pomocą /klip.⚠️")
        await self._log_system_message(logging.INFO, "No segment selected by user.")

    async def __reply_invalid_args_count(self, message: Message) -> None:
        await message.answer(
            "📝 Podaj czas w formacie `<float> <float>` lub `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub /dostosuj 1 10.5 -15.2",
        )
        await self._log_system_message(logging.INFO, "Invalid number of arguments provided by user.")

    async def __reply_invalid_interval(self, message: Message) -> None:
        await message.answer("⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.⚠️")
        await self._log_system_message(logging.INFO, "End time must be later than start time.")

    async def __reply_extraction_failure(self, message: Message, exception: FFmpegException) -> None:
        await message.answer(f"⚠️ Nie udało się zmienić klipu wideo: {exception}")
        await self._log_system_message(logging.ERROR, f"Failed to adjust video clip: {exception}")
