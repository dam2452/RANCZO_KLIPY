import logging
from pathlib import Path
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.sending_videos.manual_clip_handler_responses import (
    get_log_clip_extracted_message,
    get_log_end_time_earlier_than_start_message,
    get_log_incorrect_season_episode_format_message,
    get_log_incorrect_time_format_message,
    get_log_video_file_not_exist_message,
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
        return ["wytnij", "cut", "wyt", "pawlos"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_end_time_after_start_time,
        ]

    async def __check_end_time_after_start_time(self, message: Message) -> bool:
        content = message.text.split()

        try:
            start_seconds = minutes_str_to_seconds(content[2])
            end_seconds = minutes_str_to_seconds(content[3])
        except (InvalidSeasonEpisodeStringException, InvalidTimeStringException):
            return True

        if end_seconds <= start_seconds:
            await self.__reply_end_time_earlier_than_start(message)
            return False

        return True

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(message, 4, await self.get_response(RK.INVALID_ARGS_COUNT))

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()

        try:
            episode, start_seconds, end_seconds = self.__parse_content(content)
        except InvalidSeasonEpisodeStringException:
            return await self.__reply_incorrect_season_episode_format(message)
        except InvalidTimeStringException:
            return await self.__reply_incorrect_time_format(message)

        clip_duration = end_seconds - start_seconds
        if await self._handle_clip_duration_limit_exceeded(message, clip_duration):
            return

        video_path_str = await TranscriptionFinder.find_video_path_by_episode(
            episode.season,
            episode.get_absolute_episode_number(),
            self._logger,
        )
        if not video_path_str:
            return await self.__reply_video_file_not_exist(message, None)

        video_path = Path(video_path_str)
        if not video_path.exists():
            return await self.__reply_video_file_not_exist(message, video_path)

        output_filename = await ClipsExtractor.extract_clip(video_path, start_seconds, end_seconds, self._logger)
        await self._answer_video(message, output_filename)

        await self._log_system_message(
            logging.INFO,
            get_log_clip_extracted_message(episode, start_seconds, end_seconds),
        )

        segment_data = {
            "video_path": str(video_path),
            "start": start_seconds,
            "end": end_seconds,
            "episode_info": {
                "season": episode.season,
                "episode_number": episode.number,
            },
        }

        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment=segment_data,
            compiled_clip=None,
            clip_type=ClipType.MANUAL,
            adjusted_start_time=None,
            adjusted_end_time=None,
            is_adjusted=False,
        )

    @staticmethod
    def __parse_content(content: List[str]) -> Tuple[Episode, float, float]:
        episode = content[1]  # Format: S02E10
        start_time = content[2]  # Format: 20:30.11
        end_time = content[3]  # Format: 21:32.50

        return Episode(episode), minutes_str_to_seconds(start_time), minutes_str_to_seconds(end_time)

    async def __reply_incorrect_season_episode_format(self, message: Message) -> None:
        await self._answer_markdown(message, await self.get_response(RK.INCORRECT_SEASON_EPISODE_FORMAT))
        await self._log_system_message(logging.INFO, get_log_incorrect_season_episode_format_message())

    async def __reply_video_file_not_exist(self, message: Message, video_path: Optional[Path]) -> None:
        await self._answer_markdown(message, await self.get_response(RK.VIDEO_FILE_NOT_EXIST))
        video_path_str = str(video_path) if video_path else "Unknown"
        await self._log_system_message(logging.INFO, get_log_video_file_not_exist_message(video_path_str))

    async def __reply_incorrect_time_format(self, message: Message) -> None:
        await self._answer_markdown(message, await self.get_response(RK.INCORRECT_TIME_FORMAT))
        await self._log_system_message(logging.INFO, get_log_incorrect_time_format_message())

    async def __reply_end_time_earlier_than_start(self, message: Message) -> None:
        await self._answer(message, await self.get_response(RK.END_TIME_EARLIER_THAN_START))
        await self._log_system_message(logging.INFO, get_log_end_time_earlier_than_start_message())
