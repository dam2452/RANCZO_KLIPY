import json
import logging
from typing import (
    Dict,
    List,
    Union,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.compile_clips_handler_responses import (
    get_compilation_success_message,
    get_invalid_args_count_message,
    get_invalid_index_message,
    get_invalid_range_message,
    get_log_no_matching_segments_found_message,
    get_log_no_previous_search_results_message,
    get_max_clips_exceeded_message,
    get_no_matching_segments_found_message,
    get_no_previous_search_results_message,
)
from bot.settings import settings
from bot.video.clips_compiler import (
    ClipsCompiler,
    process_compiled_clip,
)


class CompileClipsHandler(BotMessageHandler):
    class ParseSegmentsException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ["kompiluj", "compile", "kom"]

    # pylint: disable=duplicate-code
    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, get_invalid_args_count_message())

    # pylint: enable=duplicate-code

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search or not last_search.segments:
            return await self.__reply_no_previous_search_results(message)

        segments = json.loads(last_search.segments)

        selected_segments = self.__parse_segments(content[1:], segments)

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and len(selected_segments) > settings.MAX_CLIPS_PER_COMPILATION:
            await self._answer(message,get_max_clips_exceeded_message())
            return

        total_duration = 0
        for segment in selected_segments:
            duration = (segment["end"] + settings.EXTEND_AFTER) - (segment["start"] - settings.EXTEND_BEFORE)
            total_duration += duration
            await self._log_system_message(
                logging.INFO, f"Selected clip: {segment['video_path']} "
                f"from {segment['start']} to {segment['end']} with duration {duration}",
            )
            await self._log_system_message(logging.INFO, f"Total duration: {total_duration}")

        if await self._handle_clip_duration_limit_exceeded(message, total_duration):
            return
        compiled_output = await ClipsCompiler.compile(message, selected_segments, self._logger)

        await self._answer_video(message, compiled_output)
        await process_compiled_clip(message, compiled_output, ClipType.COMPILED)

        await self._log_system_message(logging.INFO, get_compilation_success_message(message.from_user.username))

    @staticmethod
    def __parse_segments(content: List[str], segments: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
        selected_segments = []
        for index in content:
            if index.lower() == "wszystko" or index.lower() == "all":
                selected_segments.extend(
                    {"video_path": segment["video_path"], "start": segment["start"], "end": segment["end"]}
                    for segment in segments
                )
                return selected_segments

            if "-" in index:
                selected_segments.extend(CompileClipsHandler.__parse_range(index, segments))
            else:
                try:
                    selected_segments.append(CompileClipsHandler.__parse_single(index, segments))
                except CompileClipsHandler.ParseSegmentsException:
                    continue

        return selected_segments

    @staticmethod
    def __parse_range(index: str, segments: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
        try:
            start, end = [int(i) for i in index.split("-")]
            return [
                {"video_path": segments[i - 1]["video_path"], "start": segments[i - 1]["start"], "end": segments[i - 1]["end"]}
                for i in range(start, end + 1)
            ]
        except ValueError as e:
            raise CompileClipsHandler.ParseSegmentsException(get_invalid_range_message(index)) from e

    @staticmethod
    def __parse_single(index: str, segments: List[Dict[str, Union[str, float]]]) -> Dict[str, Union[str, float]]:
        try:
            segment = segments[int(index) - 1]
            return {"video_path": segment["video_path"], "start": segment["start"], "end": segment["end"]}
        except (ValueError, IndexError) as e:
            raise CompileClipsHandler.ParseSegmentsException(get_invalid_index_message(index)) from e

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await self._answer(message,get_no_previous_search_results_message())
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message())

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await self._answer(message,get_no_matching_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_matching_segments_found_message())
