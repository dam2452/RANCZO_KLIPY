import json
import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    ClipType,
    SearchHistory,
)
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.adjust_video_clip_handler_responses import (
    get_extraction_failure_log,
    get_invalid_args_count_log,
    get_invalid_interval_log,
    get_invalid_segment_log,
    get_no_previous_searches_log,
    get_no_quotes_selected_log,
    get_successful_adjustment_message,
    get_updated_segment_info_log,
)
from bot.settings import settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import (
    FFMpegException,
    get_video_duration,
)


class AdjustVideoClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["dostosuj", "adjust", "d"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 3, await self.get_response(RK.INVALID_ARGS_COUNT))


    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        segment_info = {}

        if len(content) == 4:
            last_search: SearchHistory = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
            if not last_search:
                return await self.__reply_no_previous_searches(message)
            try:
                index = int(content[1]) - 1
                segments = json.loads(last_search.segments)
                segment_info = segments[index]
            except (ValueError, IndexError):
                return await self.__reply_invalid_segment_index(message)
        elif len(content) == 3:
            last_clip = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
            if not last_clip:
                return await self.__reply_no_quotes_selected(message)

            segment_info = last_clip.segment
            if isinstance(segment_info, str):
                segment_info = json.loads(segment_info)

            await self._log_system_message(logging.INFO, f"Segment Info: {segment_info}")

        try:
            original_start_time = float(segment_info.get("start", 0))
            original_end_time = float(segment_info.get("end", 0))

            additional_start_offset = float(content[-2])
            additional_end_offset = float(content[-1])
        except (ValueError, TypeError):
            return await self.__reply_invalid_args_count(message)

        await self._log_system_message(logging.INFO, f"Additional_start_offset: {abs(additional_start_offset)}")
        await self._log_system_message(logging.INFO, f"Additional_end_offset: {abs(additional_end_offset)}")

        if await self._is_adjustment_exceeding_limits(message.from_user.id, additional_start_offset, additional_end_offset):
            await self._answer(message,await self.get_response(RK.MAX_EXTENSION_LIMIT))
            return

        start_time = max(0.0, original_start_time - additional_start_offset - settings.EXTEND_BEFORE)
        end_time = min(original_end_time + additional_end_offset + settings.EXTEND_AFTER, await get_video_duration(segment_info.get("video_path")))

        if await self._handle_clip_duration_limit_exceeded(message, end_time - start_time):
            return

        try:
            output_filename = await ClipsExtractor.extract_clip(segment_info.get("video_path"), start_time, end_time, self._logger)
            await self._answer_video(message, output_filename)

            await DatabaseManager.insert_last_clip(
                chat_id=message.chat.id,
                segment=segment_info,
                compiled_clip=None,
                clip_type=ClipType.ADJUSTED,
                adjusted_start_time=start_time,
                adjusted_end_time=end_time,
                is_adjusted=True,
            )
        except ValueError:
            return await self.__reply_invalid_interval(message)

        except FFMpegException:
            return await self.__reply_extraction_failure(message)

        await self._log_system_message(logging.INFO, get_updated_segment_info_log(message.chat.id))
        await self._log_system_message(logging.INFO, get_successful_adjustment_message(message.from_user.username))

    async def __reply_no_previous_searches(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.NO_PREVIOUS_SEARCHES))
        await self._log_system_message(logging.INFO, get_no_previous_searches_log())

    async def __reply_no_quotes_selected(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.NO_QUOTES_SELECTED))
        await self._log_system_message(logging.INFO, get_no_quotes_selected_log())

    async def __reply_invalid_args_count(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.INVALID_ARGS_COUNT))
        await self._log_system_message(logging.INFO, get_invalid_args_count_log())

    async def __reply_invalid_interval(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.INVALID_INTERVAL))
        await self._log_system_message(logging.INFO, get_invalid_interval_log())

    async def __reply_invalid_segment_index(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.INVALID_SEGMENT_INDEX))
        await self._log_system_message(logging.INFO, get_invalid_segment_log())

    async def __reply_extraction_failure(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.EXTRACTION_FAILURE,as_parent=True))
        await self._log_system_message(logging.ERROR, get_extraction_failure_log())

    @staticmethod
    async def _is_adjustment_exceeding_limits(
        user_id: int, additional_start_offset: float,
        additional_end_offset: float,
    ) -> bool:
        return (
                not await DatabaseManager.is_admin_or_moderator(user_id) and
                abs(additional_start_offset) + abs(additional_end_offset) > settings.MAX_ADJUSTMENT_DURATION
        )
