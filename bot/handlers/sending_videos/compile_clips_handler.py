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
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.compile_clips_handler_responses import (
    get_log_compilation_success_message,
    get_log_compiled_clip_is_too_long_message,
    get_log_invalid_index_message,
    get_log_invalid_range_message,
    get_log_no_matching_segments_found_message,
    get_log_no_previous_search_results_message,
    get_selected_clip_message,
)
from bot.settings import settings
from bot.video.clips_compiler import (
    ClipsCompiler,
    process_compiled_clip,
)


class CompileClipsHandler(BotMessageHandler):

    class InvalidRangeException(Exception):
        pass

    class InvalidIndexException(Exception):
        pass

    class NoMatchingSegmentsException(Exception):
        pass

    class MaxClipsExceededException(Exception):
        pass

    def get_commands(self) -> List[str]:
        return ["kompiluj", "compile", "kom"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 2, await self.get_response(RK.INVALID_ARGS_COUNT))

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        last_search = await DatabaseManager.get_last_search_by_chat_id(message.chat.id)
        if not last_search or not last_search.segments:
            return await self.__reply_no_previous_search_results(message)

        segments = json.loads(last_search.segments)
        try:
            selected_segments = await self.__parse_segments(content[1:], segments, message)
        except self.InvalidRangeException as e:
            return await self.__reply_invalid_range(message, str(e))
        except self.InvalidIndexException as e:
            return await self.__reply_invalid_index(message, str(e))
        except self.NoMatchingSegmentsException:
            return await self.__reply_no_matching_segments_found(message)
        except self.MaxClipsExceededException:
            return await self.__reply_max_clips_exceeded(message)

        if not selected_segments:
            return await self.__reply_no_matching_segments_found(message)

        if (
            not await DatabaseManager.is_admin_or_moderator(message.from_user.id)
            and len(selected_segments) > settings.MAX_CLIPS_PER_COMPILATION
        ):
            return await self.__reply_max_clips_exceeded(message)

        total_duration = 0
        for segment in selected_segments:
            duration = (segment["end"] + settings.EXTEND_AFTER) - (segment["start"] - settings.EXTEND_BEFORE)
            total_duration += duration
            await self._log_system_message(
                logging.INFO,
                get_selected_clip_message(segment["video_path"], segment["start"], segment["end"], duration),
            )

        if await self._check_clip_duration_limit(message.from_user.id, total_duration):
            return await self.__reply_clip_duration_exceeded(message)

        compiled_output = await ClipsCompiler.compile(message, selected_segments, self._logger)
        await self._answer_video(message, compiled_output)
        await process_compiled_clip(message, compiled_output, ClipType.COMPILED)
        await self._log_system_message(logging.INFO, get_log_compilation_success_message(message.from_user.username))

    async def __parse_segments(
        self ,
            content: List[str],
            segments: List[Dict[str, Union[str, float]]], message: Message,
    ) -> List[Dict[str, Union[str, float]]]:
        selected_segments = []
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
                return selected_segments
            if "-" in arg:
                selected_segments.extend(await self.__parse_range(arg, segments, message))
            else:
                selected_segments.append(await self.__parse_single(arg, segments))
        return selected_segments

    async def __parse_range(self, index: str, segments: List[Dict[str, Union[str, float]]], message: Message) -> List[Dict[str, Union[str, float]]]:
        try:
            start_str, end_str = index.split("-")
        except ValueError as exc:
            raise self.InvalidRangeException(await self.get_response(RK.INVALID_RANGE,[index])) from exc

        try:
            start, end = int(start_str), int(end_str)
        except ValueError as exc:
            raise self.InvalidRangeException(await self.get_response(RK.INVALID_RANGE,[index])) from exc

        if start > end:
            raise self.InvalidRangeException(await self.get_response(RK.INVALID_RANGE,[index]))

        num_of_clips = end - start + 1
        if not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and num_of_clips > settings.MAX_CLIPS_PER_COMPILATION:
            raise self.MaxClipsExceededException()

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
            raise self.NoMatchingSegmentsException()
        return collected


    async def __parse_single(self ,index_str: str, segments: List[Dict[str, Union[str, float]]]) -> Dict[str, Union[str, float]]:
        try:
            idx = int(index_str)
        except ValueError as exc:
            raise self.InvalidIndexException(await self.get_response(RK.INVALID_INDEX,[index_str])) from exc

        if idx < 1 or idx > len(segments):
            raise self.NoMatchingSegmentsException()

        segment = segments[idx - 1]
        return {
            "video_path": segment["video_path"],
            "start": segment["start"],
            "end": segment["end"],
        }

    @staticmethod
    async def _check_clip_duration_limit(user_id: int, total_duration: float) -> bool:
        if await DatabaseManager.is_admin_or_moderator(user_id):
            return False
        return total_duration > settings.LIMIT_DURATION

    async def __reply_no_previous_search_results(self, message: Message) -> None:
        await self._answer(message,  await self.get_response(RK.NO_PREVIOUS_SEARCH_RESULTS))
        await self._log_system_message(logging.INFO, get_log_no_previous_search_results_message())

    async def __reply_no_matching_segments_found(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.NO_MATCHING_SEGMENTS_FOUND))
        await self._log_system_message(logging.INFO, get_log_no_matching_segments_found_message())

    async def __reply_clip_duration_exceeded(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.CLIP_TIME_EXCEEDED))
        await self._log_system_message(
            logging.INFO, get_log_compiled_clip_is_too_long_message(message.from_user.username),
        )
    async def __reply_invalid_range(self, message: Message, err_msg: str) -> None:
        await self._answer(message, err_msg)
        await self._log_system_message(logging.INFO, get_log_invalid_range_message())

    async def __reply_invalid_index(self, message: Message, err_msg: str) -> None:
        await self._answer(message, err_msg)
        await self._log_system_message(logging.INFO, get_log_invalid_index_message())

    async def __reply_max_clips_exceeded(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.MAX_CLIPS_EXCEEDED))
        await self._log_system_message(logging.INFO, await self.get_response(RK.MAX_CLIPS_EXCEEDED))
