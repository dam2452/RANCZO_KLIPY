import json
import logging
import os
import tempfile
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    EpisodeInfo,
    LastClip,
    SegmentInfo,
)
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.save_clip_handler_responses import (
    get_clip_name_exists_message,
    get_clip_name_length_exceeded_message,
    get_clip_name_not_provided_message,
    get_clip_saved_successfully_message,
    get_log_clip_name_exists_message,
    get_log_clip_saved_successfully_message,
    get_log_no_segment_selected_message,
    get_no_segment_selected_message,
)
from bot.settings import settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import get_video_duration


class SaveClipHandler(BotMessageHandler):
    __SEGMENT_INFO_GETTERS: Dict[str, Callable[[Dict[str, Union[json, str]]], SegmentInfo]] = {
        "manual": (lambda last_clip_info: SegmentInfo(**last_clip_info)),
        "segment": (lambda last_clip_info: SaveClipHandler._convert_to_segment_info(last_clip_info["segment"])),
        "compiled": (lambda last_clip_info: SaveClipHandler._convert_compiled_to_segment_info(last_clip_info)),  # pylint: disable=unnecessary-lambda
        "adjusted": (lambda last_clip_info: SaveClipHandler._convert_to_segment_info_with_adjustment(last_clip_info)),  # pylint: disable=unnecessary-lambda
    }

    def get_commands(self) -> List[str]:
        return ["zapisz", "save", "z"]

    async def _do_handle(self, message: Message) -> None:
        clip_name = self.__parse_clip_name(message)

        if len(clip_name) > settings.MAX_CLIP_NAME_LENGTH:
            await message.answer(get_clip_name_length_exceeded_message())
            return

        if not clip_name:
            return await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
        if not await self.__is_clip_name_unique(message, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)
        segment_info = await self.__get_segment_info(message)
        if not segment_info:
            return await self.__reply_no_segment_selected(message)

        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip_file(segment_info)
        output_filename = output_filename.replace(" ", "_")

        duration = await get_video_duration(output_filename)
        await self.__save_clip_to_db(
            message, clip_name, output_filename, start_time, end_time, duration, is_compilation, season,
            episode_number,
        )
        await self.__reply_clip_saved_successfully(message, clip_name)

    @staticmethod
    def __parse_clip_name(message: Message) -> Optional[str]:
        content = message.text.split()
        if len(content) < 2:
            return None
        return content[1]

    @staticmethod
    async def __is_clip_name_unique(message: Message, clip_name: str) -> bool:
        return await DatabaseManager.is_clip_name_unique(message.chat.id, clip_name)

    async def __get_segment_info(self, message: Message) -> Optional[SegmentInfo]:
        last_clip_info = await self.__get_last_clip_info(message)
        if not last_clip_info:
            return None

        if last_clip_info.compiled_clip:
            return self._convert_compiled_to_segment_info(last_clip_info)

        return await self.__parse_segment_info(last_clip_info)

    async def __get_last_clip_info(self, message: Message) -> Optional[LastClip]:
        last_clip_info = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
        await self._log_system_message(logging.DEBUG, f"Full last_clip_info from DB: {last_clip_info}")

        if last_clip_info is None:
            await self._log_system_message(logging.INFO, f"No last_clip_info found for chat_id: {message.chat.id}")
            return None

        return last_clip_info

    async def __parse_segment_info(self, last_clip_info: LastClip) -> Optional[SegmentInfo]:
        segment_data = last_clip_info.segment

        if isinstance(segment_data, bytes):
            segment_info_str = segment_data.decode("utf-8")
        else:
            segment_info_str = segment_data

        segment_info_dict = await self.__decode_segment_info(segment_info_str)
        if not segment_info_dict:
            return None

        self.__apply_adjustments(segment_info_dict, last_clip_info)

        if not self.__validate_required_fields(segment_info_dict):
            return None

        return self.__create_segment_info(segment_info_dict)

    async def __decode_segment_info(self, segment_info_str: str) -> Optional[Dict]:
        try:
            return json.loads(segment_info_str)
        except json.JSONDecodeError as e:
            await self._log_system_message(logging.ERROR, f"Failed to decode JSON from segment_info_str: {e}")
            return None

    @staticmethod
    def __apply_adjustments(segment_info_dict: Dict, last_clip_info: LastClip) -> None:
        if last_clip_info.is_adjusted:
            segment_info_dict["start"] = last_clip_info.adjusted_start_time
            segment_info_dict["end"] = last_clip_info.adjusted_end_time

        if "episode_info" in segment_info_dict and isinstance(segment_info_dict["episode_info"], dict):
            episode_info_data = segment_info_dict["episode_info"]
            segment_info_dict["episode_info"] = EpisodeInfo(
                season=episode_info_data.get("season"),
                episode_number=episode_info_data.get("episode_number"),
            )

    async def __validate_required_fields(self, segment_info_dict: Dict) -> bool:
        required_fields = ["video_path", "start", "end", "episode_info"]
        missing_fields = [field for field in required_fields if field not in segment_info_dict]
        if missing_fields:
            await self._log_system_message(logging.ERROR, f"Missing required fields for SegmentInfo: {segment_info_dict}")
            return False
        return True

    @staticmethod
    def __create_segment_info(segment_info_dict: Dict) -> SegmentInfo:
        return SegmentInfo(
            video_path=segment_info_dict["video_path"],
            start=segment_info_dict["start"],
            end=segment_info_dict["end"],
            episode_info=segment_info_dict["episode_info"],
            text=segment_info_dict.get("text"),
            id=segment_info_dict.get("id"),
            author=segment_info_dict.get("author"),
            comment=segment_info_dict.get("comment"),
            tags=segment_info_dict.get("tags"),
            location=segment_info_dict.get("location"),
            actors=segment_info_dict.get("actors"),
            compiled_clip=segment_info_dict.get("compiled_clip"),
        )

    @staticmethod
    def _convert_compiled_to_segment_info(last_clip_info: LastClip) -> SegmentInfo:
        return SegmentInfo(
            video_path="default_path.mp4",
            start=0.0,
            end=last_clip_info.adjusted_end_time or 0.0,
            episode_info=EpisodeInfo(season=None, episode_number=None),
            compiled_clip=last_clip_info.compiled_clip,
        )

    @staticmethod
    def _convert_to_segment_info(segment: json) -> SegmentInfo:
        episode_info_data = segment.get("episode_info")

        if isinstance(episode_info_data, EpisodeInfo):
            episode_info_obj = episode_info_data
        else:
            episode_info_obj = EpisodeInfo(
                season=episode_info_data["season"],
                episode_number=episode_info_data["episode_number"],
            )

        segment["episode_info"] = episode_info_obj

        return SegmentInfo(**segment)

    @staticmethod
    def _convert_to_segment_info_with_adjustment(last_clip_info: Dict[str, Union[json, str]]) -> SegmentInfo:
        segment = last_clip_info["segment"]
        episode_info_data = segment.get("episode_info")

        if isinstance(episode_info_data, EpisodeInfo):
            episode_info_obj = episode_info_data
        else:
            episode_info_obj = EpisodeInfo(
                season=episode_info_data["season"],
                episode_number=episode_info_data["episode_number"],
            )

        return SegmentInfo(
            video_path=last_clip_info["video_path"],
            start=last_clip_info["start"],
            end=last_clip_info["end"],
            episode_info=episode_info_obj,
            text=segment.get("text"),
            id=segment.get("id"),
            author=segment.get("author"),
            comment=segment.get("comment"),
            tags=segment.get("tags"),
            location=segment.get("location"),
            actors=segment.get("actors"),
        )

    async def __prepare_clip_file(self, segment_info: SegmentInfo) -> Tuple[str, int, int, bool, Optional[int], Optional[int]]:
        start_time = segment_info.start - settings.EXTEND_BEFORE
        end_time = segment_info.end + settings.EXTEND_AFTER
        is_compilation = False
        season = None
        episode_number = None

        if segment_info.compiled_clip is not None:
            output_filename = self.__write_clip_to_file(segment_info.compiled_clip)
            is_compilation = True
        else:
            clip_path = segment_info.video_path
            season = segment_info.episode_info.season
            episode_number = segment_info.episode_info.episode_number
            with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4") as tmp_file:
                output_filename = tmp_file.name
            await ClipsExtractor.extract_clip(clip_path, start_time, end_time, output_filename, self._logger)

        return output_filename, start_time, end_time, is_compilation, season, episode_number

    @staticmethod
    def __write_clip_to_file(clip_data: bytes) -> str:
        with tempfile.NamedTemporaryFile(
                delete=False, delete_on_close=False, suffix=".mp4",
        ) as tmp_file:
            output_filename = tmp_file.name
        with open(output_filename, "wb") as f:
            f.write(clip_data)
        return output_filename

    @staticmethod
    async def __save_clip_to_db(
            message: Message, clip_name: str, output_filename: str, start_time: float,
            end_time: float, duration: float, is_compilation: bool, season: Optional[int],
            episode_number: Optional[int],
    ) -> None:

        with open(output_filename, "rb") as file:
            video_data = file.read()
        os.remove(output_filename)

        await DatabaseManager.save_clip(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            clip_name=clip_name,
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            is_compilation=is_compilation,
            season=season,
            episode_number=episode_number,
        )

    async def __reply_clip_name_exists(self, message: Message, clip_name: str) -> None:
        await message.answer(get_clip_name_exists_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_name_exists_message(clip_name, message.from_user.username),
        )

    async def __reply_no_segment_selected(self, message: Message) -> None:
        await message.answer(get_no_segment_selected_message())
        await self._log_system_message(
            logging.INFO,
            get_log_no_segment_selected_message(),
        )

    async def __reply_clip_saved_successfully(self, message: Message, clip_name: str) -> None:
        await message.answer(get_clip_saved_successfully_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_saved_successfully_message(clip_name, message.from_user.username),
        )
