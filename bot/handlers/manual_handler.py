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
from bot.utils.global_dicts import last_manual_clip
from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_handler import VideoManager


class ManualClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wytnij', 'cut', 'wyt', 'pawlos']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/wytnij {message.text}")

        search_transcriptions = SearchTranscriptions()
        content = message.text.split()
        if len(content) != 4:
            await self.__reply_invalid_args_count(message)
            return

        try:
            episode, start_seconds, end_seconds = self.__parse_content(content)
        except InvalidSeasonEpisodeStringException:
            return await self.__reply_incorrect_season_episode_format(message)
        except InvalidTimeStringException:
            return await self.__reply_incorrect_time_format(message)

        if end_seconds <= start_seconds:
            return await self.__reply_end_time_earlier_than_start(message)

        video_path = await search_transcriptions.find_video_path_by_episode(episode.season, episode.get_absolute_episode_number())
        if not video_path or not os.path.exists(video_path):
            return await self.__reply_video_file_not_exist(message, video_path)

        await VideoManager(self._bot).extract_and_send_clip(message.chat.id, video_path, start_seconds, end_seconds)
        await self._log_system_message(logging.INFO, f"Clip extracted and sent for command: /manual {episode} {start_seconds} {end_seconds}")

        last_manual_clip[message.chat.id] = {
            'video_path': video_path,
            'start': start_seconds,
            'end': end_seconds,
            'episode_info': {
                'season': episode.season,
                'episode_number': episode.number,
            },
        }

    @staticmethod
    def __parse_content(content: List[str]) -> Tuple[Episode, float, float]:
        episode = content[1]  # Format: S02E10
        start_time = content[2]  # Format: 20:30.11
        end_time = content[3]  # Format: 21:32.50

        return Episode(episode), minutes_str_to_seconds(start_time), minutes_str_to_seconds(end_time)

    async def __reply_invalid_args_count(
        self,
        message: Message,
    ) -> None:  # fixme tak sobie myśle czy nie zrobić w klasie bazowej jakiejś metody od chujowych argumentow bo to tez czesc wspolna
        await message.answer(
            "📋 Podaj poprawną komendę w formacie: /manual <sezon_odcinek> <czas_start> <czas_koniec>. Przykład: "
            "/manual S02E10 20:30.11",
        )
        await self._log_system_message(logging.INFO, "Incorrect command format provided by user.")

    async def __reply_incorrect_season_episode_format(self, message: Message) -> None:
        await message.answer("❌ Błędny format sezonu i odcinka. Użyj formatu SxxExx. Przykład: S02E10")
        await self._log_system_message(logging.INFO, "Incorrect season/episode format provided by user.")

    async def __reply_video_file_not_exist(self, message: Message, video_path: str) -> None:
        await message.answer("❌ Plik wideo nie istnieje dla podanego sezonu i odcinka.")
        await self._log_system_message(logging.INFO, f"Video file does not exist: {video_path}")

    async def __reply_incorrect_time_format(self, message: Message) -> None:
        await message.answer("❌ Błędny format czasu. Użyj formatu MM:SS.ms. Przykład: 20:30.11")
        await self._log_system_message(logging.INFO, "Incorrect time format provided by user.")

    async def __reply_end_time_earlier_than_start(self, message: Message) -> None:
        await message.answer("❌ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.")
        await self._log_system_message(logging.INFO, "End time must be later than start time.")
