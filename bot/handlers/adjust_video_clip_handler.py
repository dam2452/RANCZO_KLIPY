import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.database.global_dicts import (
    last_clip,
    last_search,
)
from bot.handlers.responses.adjust_video_clip_handler_responses import (
    get_extraction_failure_message,
    get_invalid_args_count_message,
    get_invalid_interval_message,
    get_invalid_segment_index_message,
    get_no_previous_searches_message,
    get_no_quotes_selected_message,
)
from bot.settings import Settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import FFMpegException


class AdjustVideoClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['dostosuj', 'adjust', 'd']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        if len(content) == 4:
            if message.chat.id not in last_search:
                return await self.__reply_no_previous_searches(message)
            try:
                index = int(content[1]) - 1
                segments = last_search[message.chat.id]['segments']
                segment_info = segments[index]
            except (ValueError, IndexError):
                return await self.__reply_invalid_segment_index(message)
        elif len(content) == 3:
            if message.chat.id not in last_clip:
                return await self.__reply_no_quotes_selected(message)
            segment_info = last_clip[message.chat.id]['segment']
        else:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        await self._log_system_message(logging.INFO, f"Segment Info: {segment_info}")

        try:
            original_start_time = float(segment_info.get('start', 0)) - float(Settings.EXTEND_BEFORE)
            original_end_time = float(segment_info.get('end', 0)) + float(Settings.EXTEND_AFTER)

            additional_start_offset = float(content[-2])
            additional_end_offset = float(content[-1])
        except (ValueError, TypeError):
            return await self.__reply_invalid_args_count(message)

        start_time = max(0, int(original_start_time - additional_start_offset))
        end_time = int(original_end_time + additional_end_offset)

        if end_time <= start_time:
            return await self.__reply_invalid_interval(message)

        try:
            await ClipsExtractor.extract_and_send_clip(segment_info.get("video_path"), message, self._bot, self._logger, start_time, end_time)
        except FFMpegException as e:
            return await self.__reply_extraction_failure(message, e)

        await self._log_system_message(logging.INFO, f"Updated segment info for chat ID '{message.chat.id}'")
        await self._log_system_message(logging.INFO, f"Video clip adjusted successfully for user '{message.from_user.username}'.")

    async def __reply_no_previous_searches(self, message: Message) -> None:
        await message.answer(get_no_previous_searches_message())
        await self._log_system_message(logging.INFO, "No previous search results found for user.")

    async def __reply_no_quotes_selected(self, message: Message) -> None:
        await message.answer(get_no_quotes_selected_message())
        await self._log_system_message(logging.INFO, "No segment selected by user.")

    async def __reply_invalid_args_count(self, message: Message) -> None:
        await message.answer(get_invalid_args_count_message())
        await self._log_system_message(logging.INFO, "Invalid number of arguments provided by user.")

    async def __reply_invalid_interval(self, message: Message) -> None:
        await message.answer(get_invalid_interval_message())
        await self._log_system_message(logging.INFO, "End time must be later than start time.")

    async def __reply_invalid_segment_index(self, message: Message) -> None:
        await message.answer(get_invalid_segment_index_message())
        await self._log_system_message(logging.INFO, "Invalid segment index provided by user.")

    async def __reply_extraction_failure(self, message: Message, exception: FFMpegException) -> None:
        await message.answer(get_extraction_failure_message(exception))
        await self._log_system_message(logging.ERROR, f"Failed to adjust video clip: {exception}")
