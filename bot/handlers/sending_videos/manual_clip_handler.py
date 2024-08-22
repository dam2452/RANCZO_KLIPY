import json
import logging
import os
from typing import (
    List,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    ClipType,
    LastClip,
)
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.sending_videos.manual_clip_handler_responses import (
    get_end_time_earlier_than_start_message,
    get_incorrect_season_episode_format_message,
    get_incorrect_time_format_message,
    get_invalid_args_count_message,
    get_log_clip_extracted_message,
    get_log_end_time_earlier_than_start_message,
    get_log_incorrect_season_episode_format_message,
    get_log_incorrect_time_format_message,
    get_log_video_file_not_exist_message,
    get_video_file_not_exist_message,
)
from bot.search.transcription_finder import TranscriptionFinder
from bot.utils.functions import (
    InvalidTimeStringException,
    minutes_str_to_seconds,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.episode import (
    Episode,
    InvalidSeasonEpisodeStringException,
)


class ManualClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wytnij', 'cut', 'wyt', 'pawlos']

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) != 4:
            await self._reply_invalid_args_count(message, get_invalid_args_count_message())
            return

        try:
            episode, start_seconds, end_seconds = self.__parse_content(content)
        except InvalidSeasonEpisodeStringException:
            return await self.__reply_incorrect_season_episode_format(message)
        except InvalidTimeStringException:
            return await self.__reply_incorrect_time_format(message)

        if end_seconds <= start_seconds:
            return await self.__reply_end_time_earlier_than_start(message)

        video_path = await TranscriptionFinder.find_video_path_by_episode(episode.season, episode.get_absolute_episode_number(), self._logger)
        if not video_path or not os.path.exists(video_path):
            return await self.__reply_video_file_not_exist(message, video_path)

        await ClipsExtractor.extract_and_send_clip(video_path, message, self._bot, self._logger, start_seconds, end_seconds)
        await self._log_system_message(logging.INFO, get_log_clip_extracted_message(episode, start_seconds, end_seconds))

        segment_data = {
            'video_path': video_path,
            'start': start_seconds,
            'end': end_seconds,
            'episode_info': {
                'season': episode.season,
                'episode_number': episode.number,
            },
        }

        last_clip = LastClip(
            id=0,
            chat_id=message.chat.id,
            segment=json.dumps(segment_data),
            compiled_clip=None,
            clip_type=ClipType.MANUAL,
            adjusted_start_time=None,
            adjusted_end_time=None,
            is_adjusted=False,
            timestamp=None,
        )

        await DatabaseManager.insert_last_clip(last_clip)

    @staticmethod
    def __parse_content(content: List[str]) -> Tuple[Episode, float, float]:
        episode = content[1]  # Format: S02E10
        start_time = content[2]  # Format: 20:30.11
        end_time = content[3]  # Format: 21:32.50

        return Episode(episode), minutes_str_to_seconds(start_time), minutes_str_to_seconds(end_time)

    async def __reply_incorrect_season_episode_format(self, message: Message) -> None:
        await message.answer(get_incorrect_season_episode_format_message())
        await self._log_system_message(logging.INFO, get_log_incorrect_season_episode_format_message())

    async def __reply_video_file_not_exist(self, message: Message, video_path: str) -> None:
        await message.answer(get_video_file_not_exist_message())
        await self._log_system_message(logging.INFO, get_log_video_file_not_exist_message(video_path))

    async def __reply_incorrect_time_format(self, message: Message) -> None:
        await message.answer(get_incorrect_time_format_message())
        await self._log_system_message(logging.INFO, get_log_incorrect_time_format_message())

    async def __reply_end_time_earlier_than_start(self, message: Message) -> None:
        await message.answer(get_end_time_earlier_than_start_message())
        await self._log_system_message(logging.INFO, get_log_end_time_earlier_than_start_message())
