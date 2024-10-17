import json
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
)
from bot.responses.sending_videos.select_clip_handler_responses import (
    get_invalid_args_count_message,
    get_invalid_segment_number_message,
    get_log_invalid_segment_number_message,
    get_log_no_previous_search_message,
    get_log_segment_selected_message,
    get_no_previous_search_message,
)
from bot.utils.functions import (
    check_clip_duration_and_permissions,
    validate_argument_count,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import FFMpegException


class SelectClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["wybierz", "select", "w"]

    # pylint: disable=R0801
    def _get_validator_functions(self) -> List[Callable[[Message], Awaitable[bool]]]:
        return [
            self._validate_argument_count,
        ]

    async def _validate_argument_count(self, message: Message) -> bool:
        return await validate_argument_count(
            message, 2, self._reply_invalid_args_count,
            get_invalid_args_count_message(),
        )

    # pylint: enable=R0801
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

        result = await check_clip_duration_and_permissions(segment, message)
        if result is None:
            return
        start_time, end_time = result

        try:
            await ClipsExtractor.extract_and_send_clip(
                segment["video_path"], message, self._bot, self._logger,
                start_time, end_time,
            )
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
        await message.answer(get_no_previous_search_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_message())

    async def __reply_extraction_failure(self, message: Message, exception: FFMpegException) -> None:
        await message.answer(get_extraction_failure_message())
        await self._log_system_message(logging.ERROR, get_log_extraction_failure_message(exception))

    async def __reply_invalid_segment_number(self, message: Message, segment_number: int) -> None:
        await message.answer(get_invalid_segment_number_message())
        await self._log_system_message(logging.WARNING, get_log_invalid_segment_number_message(segment_number))
