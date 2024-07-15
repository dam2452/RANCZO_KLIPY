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
from bot_message_handler import BotMessageHandler

from bot.handlers.responses.save_clip_handler_responses import (
    get_clip_name_exists_message,
    get_clip_saved_successfully_message,
    get_failed_to_verify_clip_length_message,
    get_log_clip_name_exists_message,
    get_log_clip_saved_successfully_message,
    get_log_failed_to_verify_clip_length_message,
    get_log_no_segment_selected_message,
    get_no_segment_selected_message,
)
from bot.utils.database import DatabaseManager
from bot.utils.global_dicts import last_clip
from bot.utils.segment_info import SegmentInfo
from bot.utils.video_manager import VideoProcessor


class SaveClipHandler(BotMessageHandler):
    __SEGMENT_INFO_GETTERS: Dict[str, Callable[[Dict[str, Union[json, str]]], SegmentInfo]] = {
        "manual": (lambda last_clip_info: SegmentInfo(**last_clip_info)),
        "segment": (lambda last_clip_info: SegmentInfo(**last_clip_info['segment'])),
        "compiled": (lambda last_clip_info: SegmentInfo(**last_clip_info['compiled_clip'])),
    }

    def get_commands(self) -> List[str]:
        return ['zapisz', 'save', 'z']

    async def _do_handle(self, message: Message) -> None:
        clip_name = self.__parse_clip_name(message)

        if not clip_name:
            return await self._reply_invalid_args_count(message, "📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu")

        if not await self.__is_clip_name_unique(message, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)

        segment_info = self.__get_segment_info(message)
        if not segment_info:
            return await self.__reply_no_segment_selected(message)

        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip_file(segment_info)
        actual_duration = await self.__get_actual_duration(output_filename)
        if actual_duration is None:
            os.remove(output_filename)
            return await self.__reply_failed_to_verify_clip_length(message, clip_name)

        await self.__save_clip_to_db(message, clip_name, output_filename, start_time, end_time, is_compilation, season, episode_number)
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

    @staticmethod
    def __get_segment_info(message: Message) -> Optional[SegmentInfo]:
        last_clip_info = last_clip.get(message.chat.id)
        if last_clip_info is None:
            return None

        return SaveClipHandler.__SEGMENT_INFO_GETTERS[last_clip_info['type']](last_clip_info)

    async def __prepare_clip_file(self, segment_info: SegmentInfo) -> Tuple[str, int, int, bool, Optional[int], Optional[int]]:
        start_time = 0
        end_time = 0
        is_compilation = False
        season = None
        episode_number = None

        if segment_info.compiled_clip:
            output_filename = self.__write_clip_to_file(segment_info.compiled_clip)
            is_compilation = True
        elif segment_info.expanded_clip:
            output_filename = self.__write_clip_to_file(segment_info.expanded_clip)
            start_time = segment_info.expanded_start
            end_time = segment_info.expanded_end
            season = segment_info.episode_info.season
            episode_number = segment_info.episode_info.episode_number
        else:
            clip_path = segment_info.video_path
            start_time = segment_info.start
            end_time = segment_info.end
            season = segment_info.episode_info.season
            episode_number = segment_info.episode_info.episode_number
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name  # pylint: disable=consider-using-with
            await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)

        return output_filename, start_time, end_time, is_compilation, season, episode_number

    @staticmethod
    def __write_clip_to_file(clip_data: bytes) -> str:
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name  # pylint: disable=consider-using-with
        with open(output_filename, 'wb') as f:
            f.write(clip_data)
        return output_filename

    @staticmethod
    async def __get_actual_duration(output_filename: str) -> Optional[int]:
        actual_duration = await VideoProcessor.get_video_duration(output_filename)
        return actual_duration

    @staticmethod
    async def __save_clip_to_db(
        message: Message, clip_name: str, output_filename: str, start_time: int,
        end_time: int, is_compilation: bool, season: Optional[int],
        episode_number: Optional[int],
    ) -> None:
        with open(output_filename, 'rb') as file:
            video_data = file.read()
        os.remove(output_filename)
        await DatabaseManager.save_clip(
            chat_id=message.chat.id,
            username=message.from_user.username,
            clip_name=clip_name,
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
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

    async def __reply_failed_to_verify_clip_length(self, message: Message, clip_name: str) -> None:
        await message.answer(get_failed_to_verify_clip_length_message())
        await self._log_system_message(
            logging.ERROR,
            get_log_failed_to_verify_clip_length_message(clip_name, message.from_user.username),
        )

    async def __reply_clip_saved_successfully(self, message: Message, clip_name: str) -> None:
        await message.answer(get_clip_saved_successfully_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_saved_successfully_message(clip_name, message.from_user.username),
        )
