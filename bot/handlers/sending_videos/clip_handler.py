import logging
from typing import (
    Awaitable,
    Callable,
    List,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.bot_message_handler_responses import (
    get_extraction_failure_message,
    get_log_extraction_failure_message,
    get_log_no_segments_found_message,
)
from bot.responses.sending_videos.clip_handler_responses import (
    get_log_clip_success_message,
    get_log_segment_saved_message,
    get_message_too_long_message,
    get_no_quote_provided_message,
    get_no_segments_found_message,
)
from bot.search.transcription_finder import TranscriptionFinder
from bot.settings import settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import FFMpegException


class ClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["klip", "clip", "k"]

    def _get_validator_functions(self) -> List[Callable[[Message], Awaitable[bool]]]:
        return [
            self._validate_message_length,
            self._validate_user_permissions,
        ]

    async def _validate_message_length(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_no_quote_provided_message())
            return False
        return True
    @staticmethod
    async def _validate_user_permissions(message: Message) -> bool:
        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and len(message.text) > settings.MAX_SEARCH_QUERY_LENGTH:
            await message.answer(get_message_too_long_message())
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        quote = " ".join(content[1:])

        segments = await TranscriptionFinder.find_segment_by_quote(quote, self._logger, return_all=False)

        if not segments:
            return await self.__reply_no_segments_found(message, quote)
        segment = segments[0] if isinstance(segments, list) else segments

        start_time = max(0, segment["start"] - settings.EXTEND_BEFORE)
        end_time = segment["end"] + settings.EXTEND_AFTER

        if await self.handle_clip_duration_limit_exceeded(message, end_time - start_time):
            return

        try:
            await ClipsExtractor.extract_and_send_clip(segment["video_path"], message, self._bot, self._logger, start_time, end_time)
        except FFMpegException as e:
            return await self.__reply_extraction_failed(message, e)

        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment=segment,
            compiled_clip=None,
            clip_type=ClipType.SINGLE,
            adjusted_start_time=start_time,
            adjusted_end_time=end_time,
            is_adjusted=False,
        )

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
