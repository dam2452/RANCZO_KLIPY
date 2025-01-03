import json
import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.bot_message_handler_responses import (
    get_extraction_failure_message,
    get_log_extraction_failure_message,
)
from bot.responses.sending_videos.select_clip_handler_responses import (
    get_log_invalid_segment_number_message,
    get_log_no_previous_search_message,
    get_log_segment_selected_message,
)
from bot.settings import settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import FFMpegException


class SelectClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["wybierz", "select", "w"]

    # pylint: disable=duplicate-code
    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, await self.get_response(RK.INVALID_ARGS_COUNT))


    # pylint: enable=duplicate-code
    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search:
            return await self.__reply_no_previous_search(message)

        index = int(content[1])
        segments = json.loads(last_search.segments)

        if index not in range(1, len(segments) + 1):
            return await self.__reply_invalid_segment_number(message, index)

        segment = segments[index - 1]

        start_time = max(0, segment["start"] - settings.EXTEND_BEFORE)
        end_time = segment["end"] + settings.EXTEND_AFTER

        if await self._handle_clip_duration_limit_exceeded(message, end_time - start_time):
            return

        try:
            output_filename = await ClipsExtractor.extract_clip(segment["video_path"], start_time, end_time, self._logger)
            await self._answer_video(message, output_filename)
        except FFMpegException as e:
            return await self.__reply_extraction_failure(message, e)

        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment=segment,
            compiled_clip=None,
            clip_type=ClipType.SELECTED,
            adjusted_start_time=None,
            adjusted_end_time=None,
            is_adjusted=False,
        )

        await self._log_system_message(
            logging.INFO,
            get_log_segment_selected_message(segment["id"], message.from_user.username),
        )

    async def __reply_no_previous_search(self, message: Message) -> None:
        await self._answer(message,await self.get_response(RK.NO_PREVIOUS_SEARCH))
        await self._log_system_message(logging.INFO, get_log_no_previous_search_message())

    async def __reply_extraction_failure(self, message: Message, exception: FFMpegException) -> None:
        await self._answer(message,get_extraction_failure_message())
        await self._log_system_message(logging.ERROR, get_log_extraction_failure_message(exception))

    async def __reply_invalid_segment_number(self, message: Message, segment_number: int) -> None:
        await self._answer(message,await self.get_response(RK.INVALID_SEGMENT_NUMBER))
        await self._log_system_message(logging.WARNING, get_log_invalid_segment_number_message(segment_number))
