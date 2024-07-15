import logging
import os
from typing import (
    List,
    Tuple,
)

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.functions import (
    Episode,
    InvalidSeasonEpisodeStringException,
    InvalidTimeStringException,
    minutes_str_to_seconds,
)
from bot.utils.global_dicts import last_clip
from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_manager import VideoManager
from bot.handlers.responses.manual_clip_handler_responses import (
    get_invalid_args_count_message,
    get_incorrect_season_episode_format_message,
    get_video_file_not_exist_message,
    get_incorrect_time_format_message,
    get_end_time_earlier_than_start_message,
    get_log_incorrect_season_episode_format_message,
    get_log_video_file_not_exist_message,
    get_log_incorrect_time_format_message,
    get_log_end_time_earlier_than_start_message,
    get_log_clip_extracted_message
)


class ManualClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wytnij', 'cut', 'wyt', 'pawlos']

    async def _do_handle(self, message: Message) -> None:
        command = self.get_commands()[0]
        await self._log_user_activity(message.from_user.username, f"/{command} {message.text}")

        content = message.text.split()
        if len(content) != 4:
            await self._reply_invalid_args_count(
                message,
                get_invalid_args_count_message(),
            )
            return

        try:
            episode, start_seconds, end_seconds = self.__parse_content(content)
        except InvalidSeasonEpisodeStringException:
            return await self.__reply_incorrect_season_episode_format(message)
        except InvalidTimeStringException:
            return await self.__reply_incorrect_time_format(message)

        if end_seconds <= start_seconds:
            return await self.__reply_end_time_earlier_than_start(message)

        video_path = await SearchTranscriptions.find_video_path_by_episode(episode.season, episode.get_absolute_episode_number())
        if not video_path or not os.path.exists(video_path):
            return await self.__reply_video_file_not_exist(message, video_path)

        await VideoManager.extract_and_send_clip(message.chat.id, video_path, start_seconds, end_seconds, self._bot)
        await self._log_system_message(
            logging.INFO,
            get_log_clip_extracted_message(episode, start_seconds, end_seconds),
        )

        last_clip[message.chat.id] = {
            'video_path': video_path,
            'start': start_seconds,
            'end': end_seconds,
            'episode_info': {
                'season': episode.season,
                'episode_number': episode.number,
            },
            'type': 'manual',
        }

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
        await message.answer(get_video_file_not_exist_message(video_path))
        await self._log_system_message(logging.INFO, get_log_video_file_not_exist_message(video_path))

    async def __reply_incorrect_time_format(self, message: Message) -> None:
        await message.answer(get_incorrect_time_format_message())
        await self._log_system_message(logging.INFO, get_log_incorrect_time_format_message())

    async def __reply_end_time_earlier_than_start(self, message: Message) -> None:
        await message.answer(get_end_time_earlier_than_start_message())
        await self._log_system_message(logging.INFO, get_log_end_time_earlier_than_start_message())
