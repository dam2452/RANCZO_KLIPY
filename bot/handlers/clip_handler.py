import logging
from typing import List

from aiogram.types import Message
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.clip_handler_responses import (
    get_extraction_failure_message,
    get_log_clip_success_message,
    get_log_extraction_failure_message,
    get_log_no_segments_found_message,
    get_log_segment_saved_message,
    get_no_quote_provided_message,
    get_no_segments_found_message,
)
from bot.settings import Settings
from bot.utils.global_dicts import last_clip
from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_manager import VideoManager
from bot.utils.video_utils import FFmpegException


class ClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['klip', 'clip', 'k']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_quote_provided_message())

        quote = ' '.join(content[1:])

        segments = await SearchTranscriptions.find_segment_by_quote(quote, return_all=False)

        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        segment = segments[0] if isinstance(segments, list) else segments
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end_time = segment['end'] + Settings.EXTEND_AFTER

        try:
            await VideoManager.extract_and_send_clip(message.chat.id, video_path, start_time, end_time, self._bot)
        except FFmpegException as e:
            return await self.__reply_extraction_failure(message, e)

        last_clip[message.chat.id] = {'segment': segment, 'type': 'segment'}
        await self.__log_segment_and_clip_success(message.chat.id, message.from_user.username)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __reply_extraction_failure(self, message: Message, exception: FFmpegException) -> None:
        await message.answer(get_extraction_failure_message())
        await self._log_system_message(logging.ERROR, get_log_extraction_failure_message(exception))

    async def __log_segment_and_clip_success(self, chat_id: int, username: str) -> None:
        await self._log_system_message(logging.INFO, get_log_segment_saved_message(chat_id))
        await self._log_system_message(logging.INFO, get_log_clip_success_message(username))
