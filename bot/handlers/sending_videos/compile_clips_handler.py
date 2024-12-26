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
    get_clip_time_message,
    get_invalid_args_count_message,
    get_invalid_index_message,
    get_invalid_range_message,
    get_log_compilation_success_message,
    get_log_compiled_clip_is_too_long_message,
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
        """Raised when there is an error parsing the segments from the provided arguments."""

    class InvalidRangeException(Exception):
        """Raised when the range is reversed (e.g., 5-3) or improperly formatted."""

    class NoMatchingSegmentsException(Exception):
        """Raised when there are no matching segments within the provided range."""

    def get_commands(self) -> List[str]:
        return ["compile", "kompiluj", "kom"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, get_invalid_args_count_message())

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search or not last_search.segments:
            return await self.__reply_no_previous_search_results(message)

        segments = json.loads(last_search.segments)
        selected_segments, errors = self.__parse_segments(content[1:], segments)

        if errors:
            return await self._answer(message, "\n".join(errors))

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        if (
            not await DatabaseManager.is_admin_or_moderator(message.from_user.id)
            and len(selected_segments) > settings.MAX_CLIPS_PER_COMPILATION
        ):
            return await self._answer(message, get_max_clips_exceeded_message())

        total_duration = 0
        for segment in selected_segments:
            duration = (
                (segment["end"] + settings.EXTEND_AFTER)
                - (segment["start"] - settings.EXTEND_BEFORE)
            )
            total_duration += duration
            await self._log_system_message(
                logging.INFO,
                f"Selected clip: {segment['video_path']} "
                f"from {segment['start']} to {segment['end']} with duration {duration}",
            )

        if await self._check_clip_duration_limit(message, total_duration):
            return

        compiled_output = await ClipsCompiler.compile(message, selected_segments, self._logger)
        await self._answer_video(message, compiled_output)
        await process_compiled_clip(message, compiled_output, ClipType.COMPILED)

        await self._log_system_message(
            logging.INFO,
            get_log_compilation_success_message(message.from_user.username),
        )

    @staticmethod
    def __parse_segments(
        content: List[str],
        segments: List[Dict[str, Union[str, float]]],
    ) -> (List[Dict[str, Union[str, float]]], List[str]):
        selected_segments = []
        errors = []

        for arg in content:
            if arg.lower() in {"all", "wszystko"}:
                selected_segments.extend(
                    {
                        "video_path": s["video_path"],
                        "start": s["start"],
                        "end": s["end"],
                    }
                    for s in segments
                )
                return selected_segments, errors

            if "-" in arg:
                try:
                    selected_segments.extend(CompileClipsHandler.__parse_range(arg, segments))
                except CompileClipsHandler.InvalidRangeException as exc:
                    errors.append(str(exc))
                except CompileClipsHandler.NoMatchingSegmentsException as exc:
                    errors.append(str(exc))
            else:
                try:
                    selected_segments.append(CompileClipsHandler.__parse_single(arg, segments))
                except CompileClipsHandler.InvalidRangeException as exc:
                    errors.append(str(exc))
                except CompileClipsHandler.NoMatchingSegmentsException as exc:
                    errors.append(str(exc))

        return selected_segments, errors

    @staticmethod
    def __parse_range(index: str, segments: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
        start_str, end_str = index.split("-")
        try:
            start, end = int(start_str), int(end_str)
        except ValueError as exc:
            raise CompileClipsHandler.InvalidRangeException(
                get_invalid_range_message(index),
            ) from exc

        if start > end:
            raise CompileClipsHandler.InvalidRangeException(get_invalid_range_message(index))

        num_of_clips = end - start + 1
        if num_of_clips > settings.MAX_CLIPS_PER_COMPILATION:
            raise CompileClipsHandler.InvalidRangeException(get_max_clips_exceeded_message())

        collected = []
        for i in range(start, end + 1):
            try:
                segment = segments[i - 1]
                collected.append({
                    "video_path": segment["video_path"],
                    "start": segment["start"],
                    "end": segment["end"],
                })
            except IndexError:
                pass

        if not collected:
            raise CompileClipsHandler.NoMatchingSegmentsException(get_no_matching_segments_found_message())

        return collected

    @staticmethod
    def __parse_single(index: str, segments: List[Dict[str, Union[str, float]]]) -> Dict[str, Union[str, float]]:
        try:
            idx = int(index)
            segment = segments[idx - 1]
            return {
                "video_path": segment["video_path"],
                "start": segment["start"],
                "end": segment["end"],
            }
        except ValueError as exc:
            raise CompileClipsHandler.InvalidRangeException(
                get_invalid_index_message(index),
            ) from exc
        except IndexError as exc:
            raise CompileClipsHandler.NoMatchingSegmentsException(
                get_no_matching_segments_found_message(),
            ) from exc

    async def _check_clip_duration_limit(self, message: Message, total_duration: float) -> bool:
        if await DatabaseManager.is_admin_or_moderator(message.from_user.id):
            return False
        limit = settings.LIMIT_DURATION
        if total_duration > limit:
            await self.__reply_clip_duration_exceeded(message)
            return True
        return False

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await self._answer(message, get_no_previous_search_results_message())
        await self._log_system_message(logging.INFO,  get_log_no_previous_search_results_message())

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await self._answer(message, get_no_matching_segments_found_message())
        await self._log_system_message(logging.INFO, get_log_no_matching_segments_found_message())

    async def __reply_clip_duration_exceeded(self, message: Message) -> None:
        await self._answer(message, get_clip_time_message())
        await self._log_system_message(logging.INFO, get_log_compiled_clip_is_too_long_message(message.from_user.username))
