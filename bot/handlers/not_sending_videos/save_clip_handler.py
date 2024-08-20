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
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.save_clip_handler_responses import (
    get_clip_name_exists_message,
    get_clip_name_not_provided_message,
    get_clip_saved_successfully_message,
    get_log_clip_name_exists_message,
    get_log_clip_saved_successfully_message,
    get_log_no_segment_selected_message,
    get_no_segment_selected_message,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.segment_info import (
    EpisodeInfo,
    SegmentInfo,
)
from bot.video.utils import get_video_duration
from bot.settings import settings

class SaveClipHandler(BotMessageHandler):
    __SEGMENT_INFO_GETTERS: Dict[str, Callable[[Dict[str, Union[json, str]]], SegmentInfo]] = {
        "manual": (lambda last_clip_info: SegmentInfo(**last_clip_info)),
        "segment": (lambda last_clip_info: SaveClipHandler._convert_to_segment_info(last_clip_info['segment'])),
        "compiled": (lambda last_clip_info: SegmentInfo(**last_clip_info['compiled_clip'])),
        "adjusted": (lambda last_clip_info: SaveClipHandler._convert_to_segment_info_with_adjustment(last_clip_info)),  # pylint: disable=unnecessary-lambda
    }

    def get_commands(self) -> List[str]:
        return ['zapisz', 'save', 'z']

    async def _do_handle(self, message: Message) -> None:
        clip_name = self.__parse_clip_name(message)
        if not clip_name:
            return await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
        if not await self.__is_clip_name_unique(message, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)
        segment_info = await self.__get_segment_info(message)
        if not segment_info:
            return await self.__reply_no_segment_selected(message)

        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip_file(segment_info)
        output_filename.replace(" ", "_")

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
        last_clip_info = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)

        logging.debug("Full last_clip_info from DB: %s", last_clip_info)

        if last_clip_info is None:
            logging.info("No last_clip_info found for chat_id: %s", message.chat.id)
            return None

        segment_data = last_clip_info['segment']
        compiled_clip_data = last_clip_info['compiled_clip']

        logging.debug("Raw segment data: %s", segment_data)
        logging.debug("Raw compiled clip data: %s", compiled_clip_data)

        if segment_data is None and compiled_clip_data is not None:
            logging.info("Using compiled clip data for chat_id: %s", message.chat.id)
            return SegmentInfo(compiled_clip=compiled_clip_data)

        if segment_data is None:
            logging.error("Segment data is None for chat_id: %s", message.chat.id)
            return None

        if isinstance(segment_data, bytes):
            segment_info_str = segment_data.decode('utf-8')
        else:
            segment_info_str = segment_data

        try:
            segment_info_dict = json.loads(segment_info_str)
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON from segment_info_str: %s", e)
            return None

        adjusted_start_time = last_clip_info.get('adjusted_start_time')
        adjusted_end_time = last_clip_info.get('adjusted_end_time')
        is_adjusted = last_clip_info.get('is_adjusted', False)

        if is_adjusted and adjusted_start_time is not None and adjusted_end_time is not None:
            segment_info_dict['start'] = adjusted_start_time
            segment_info_dict['end'] = adjusted_end_time

        if 'episode_info' in segment_info_dict and isinstance(segment_info_dict['episode_info'], dict):
            episode_info_data = segment_info_dict['episode_info']
            episode_info = EpisodeInfo(
                season=episode_info_data['season'],
                episode_number=episode_info_data['episode_number'],
            )
            segment_info_dict['episode_info'] = episode_info

        return SegmentInfo(**segment_info_dict)

    @staticmethod
    def _convert_to_segment_info(segment: json) -> SegmentInfo:
        episode_info_data = segment.get('episode_info')

        if isinstance(episode_info_data, EpisodeInfo):
            episode_info_obj = episode_info_data
        else:
            episode_info_obj = EpisodeInfo(
                season=episode_info_data['season'],
                episode_number=episode_info_data['episode_number'],
            )

        segment['episode_info'] = episode_info_obj

        return SegmentInfo(**segment)

    @staticmethod
    def _convert_to_segment_info_with_adjustment(last_clip_info: Dict[str, Union[json, str]]) -> SegmentInfo:
        segment = last_clip_info['segment']
        episode_info_data = segment.get('episode_info')

        if isinstance(episode_info_data, EpisodeInfo):
            episode_info_obj = episode_info_data
        else:
            episode_info_obj = EpisodeInfo(
                season=episode_info_data['season'],
                episode_number=episode_info_data['episode_number'],
            )

        return SegmentInfo(
            video_path=last_clip_info['video_path'],
            start=last_clip_info['start'],
            end=last_clip_info['end'],
            episode_info=episode_info_obj,
            text=segment.get('text'),
            id=segment.get('id'),
            author=segment.get('author'),
            comment=segment.get('comment'),
            tags=segment.get('tags'),
            location=segment.get('location'),
            actors=segment.get('actors'),
        )

    async def __prepare_clip_file(self, segment_info: SegmentInfo) -> Tuple[str, int, int, bool, Optional[int], Optional[int]]:
        start_time = segment_info.start  - settings.EXTEND_BEFORE
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
        with open(output_filename, 'wb') as f:
            f.write(clip_data)
        return output_filename

    @staticmethod
    async def __save_clip_to_db(
            message: Message, clip_name: str, output_filename: str, start_time: float,
            end_time: float, duration: float, is_compilation: bool, season: Optional[int],
            episode_number: Optional[int],
    ) -> None:

        with open(output_filename, 'rb') as file:
            video_data = file.read()
        os.remove(output_filename)

        user_id = await DatabaseManager.get_user_id_by_username(message.from_user.username)

        await DatabaseManager.save_clip(
            chat_id=message.chat.id,
            user_id=user_id,
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
