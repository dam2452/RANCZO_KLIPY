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
from bot.database.global_dicts import last_clip
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.save_clip_handler_responses import (
    get_clip_name_exists_message,
    get_clip_saved_successfully_message,
    get_log_clip_name_exists_message,
    get_log_clip_saved_successfully_message,
    get_log_no_segment_selected_message,
    get_no_segment_selected_message,
    get_clip_name_not_provided_message,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.segment_info import (
    EpisodeInfo,
    SegmentInfo,
)
from bot.video.utils import get_video_duration


class SaveClipHandler(BotMessageHandler):
    __SEGMENT_INFO_GETTERS: Dict[str, Callable[[Dict[str, Union[json, str]]], SegmentInfo]] = {
        "manual": (lambda last_clip_info: SegmentInfo(**last_clip_info)),
        "segment": (lambda last_clip_info: SaveClipHandler._convert_to_segment_info(last_clip_info['segment'])),
        "compiled": (lambda last_clip_info: SegmentInfo(**last_clip_info['compiled_clip'])),
    }

    def get_commands(self) -> List[str]:
        return ['zapisz', 'save', 'z']

    async def _do_handle(self, message: Message) -> None:
        clip_name = self.__parse_clip_name(message)
        print("1111111111111111111111111111111111111111111111111111111111111")
        if not clip_name:
            return await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
        print("22222222222222222222222222222222222222222222222222222222222222")
        if not await self.__is_clip_name_unique(message, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)
        print("33333333333333333333333333333333333333333333333333333333333333333333")
        segment_info = self.__get_segment_info(message)
        print(f"4444444444444444444444444444444444segment_info {segment_info}") #fixme tu się dziwka wypierdala
        if not segment_info:
            return await self.__reply_no_segment_selected(message)

        print(f"555555555555555555555555555555555555segment_info {segment_info}")

        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip_file(segment_info)
        print("-------------------------------------------------------------------------------")
        print(f"output_filename {output_filename}")
        print(f"start_time {start_time}")
        print(f"end_time {end_time}")
        print(f"is_compilation {is_compilation}")
        print(f"season {season}")
        print(f"episode_number {episode_number}")
        print("-------------------------------------------------------------------------------")
        duration = await get_video_duration(output_filename)  #fixme jak mu tego loggera dać narazie wydupcam XDD , self._logger
        print(f"duration {duration}")
        print("-------------------------------------------------------------------------------")
        await self.__save_clip_to_db(message, clip_name, output_filename, start_time, end_time, duration, is_compilation, season, episode_number)
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
        print(f"last_clip_info {last_clip_info}")
        if last_clip_info is None:
            return None

        if 'segment' in last_clip_info and 'episode_info' not in last_clip_info['segment']:
            last_clip_info['segment']['episode_info'] = {}

        # Konwersja słownika episode_info na instancję EpisodeInfo, jeśli jest w formie słownika
        if isinstance(last_clip_info['segment']['episode_info'], dict):
            episode_info_data = last_clip_info['segment']['episode_info']
            # Filtrowanie tylko wymaganych argumentów dla EpisodeInfo
            filtered_episode_info = {k: episode_info_data[k] for k in ['season', 'episode_number'] if k in episode_info_data}
            last_clip_info['segment']['episode_info'] = EpisodeInfo(**filtered_episode_info)

        print(f"last_clip_info2 {last_clip_info}")
        print(
            f"SaveClipHandler.__SEGMENT_INFO_GETTERS[last_clip_info['type']](last_clip_info) {SaveClipHandler.__SEGMENT_INFO_GETTERS[last_clip_info['type']](last_clip_info)}")
        return SaveClipHandler.__SEGMENT_INFO_GETTERS[last_clip_info['type']](last_clip_info)

    @staticmethod
    def _convert_to_segment_info(segment: dict) -> SegmentInfo:
        print(f"_convert_to_segment_info segment1 {segment}")
        episode_info_data = segment.get('episode_info')

        # Sprawdzanie, czy episode_info_data jest instancją EpisodeInfo
        if isinstance(episode_info_data, EpisodeInfo):
            episode_info_obj = episode_info_data
        else:
            # Jeśli to słownik, konwersja na instancję EpisodeInfo
            print(f"_convert_to_segment_info episode_info_data {episode_info_data}")
            episode_info_obj = EpisodeInfo(
                season=episode_info_data['season'],
                episode_number=episode_info_data['episode_number']
            )

        print(f"_convert_to_segment_info episode_info_obj {episode_info_obj}")
        segment['episode_info'] = episode_info_obj

        print(f"_convert_to_segment_info2 segment {SegmentInfo(**segment)}")
        return SegmentInfo(**segment)

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
            with tempfile.NamedTemporaryFile(
                delete=False, delete_on_close=False, suffix=".mp4",
            ) as tmp_file:
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
        await DatabaseManager.save_clip(
            chat_id=message.chat.id,
            username=message.from_user.username,
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
