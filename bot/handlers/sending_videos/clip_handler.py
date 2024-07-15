import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.bot_message_handler_responses import (
    get_extraction_failure_message,
    get_log_extraction_failure_message,
    get_log_no_segments_found_message,
)
from bot.responses.sending_videos.clip_handler_responses import (
    get_log_clip_success_message,
    get_log_segment_saved_message,
    get_no_quote_provided_message,
    get_no_segments_found_message,
)
from bot.search.transcription_finder import TranscriptionFinder
from bot.settings import Settings
from bot.utils.functions import update_last_clip
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import FFMpegException


class ClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['klip', 'clip', 'k']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_no_quote_provided_message())

        quote = ' '.join(content[1:])

        segments = await TranscriptionFinder.find_segment_by_quote(quote, return_all=False)

        if not segments:
            return await self.__reply_no_segments_found(message, quote)

        segment = segments[0] if isinstance(segments, list) else segments
        start_time = max(0, segment['start'] - Settings.EXTEND_BEFORE)
        end_time = segment['end'] + Settings.EXTEND_AFTER
        try:
            await ClipsExtractor.extract_and_send_clip(segment['video_path'], message, self._bot, self._logger, start_time, end_time)
        except FFMpegException as e:
            return await self.__reply_extraction_failed(message, e)

        update_last_clip(segment, start_time, end_time, message)

        await self.__log_segment_and_clip_success(message.chat.id, message.from_user.username)

    async def __reply_no_segments_found(self, message: Message, quote: str) -> None:
        await message.answer(get_no_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_segments_found_message(quote))

    async def __reply_extraction_failed(self, message: Message, exception: FFMpegException) -> None:
        await message.answer(get_extraction_failure_message())
        await self._log_system_message(logging.ERROR, get_log_extraction_failure_message(exception))

    async def __log_segment_and_clip_success(self, chat_id: int, username: str) -> None:
        await self._log_system_message(logging.INFO, get_log_segment_saved_message(chat_id))
        await self._log_system_message(logging.INFO, get_log_clip_success_message(username))
