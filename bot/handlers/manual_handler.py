import json
import logging
import os
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message


from bot_message_handler import BotMessageHandler

from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_handler import VideoManager

last_manual_clip: Dict[int, json] = {} #fixme z tymi zmeinnymi globalnymi jak tak najebane wszedzię XD


def minutes_str_to_seconds(time_str: str) -> Optional[float]: #fixme te dwie funkcje zdaje się że też się gdzieś powtarzają to gdzie je dać do utlis.py?
    """ Convert time string in the format MM:SS.ms to seconds """
    try:
        minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    except ValueError:
        return None


def adjust_episode_number(absolute_episode: int) -> Optional[Tuple[int, int]]:
    """ Adjust the absolute episode number to season and episode format """
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode


class ManualClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wytnij', 'cut', 'wyt', 'pawlos']

    def get_action_name(self) -> str:
        return "manual_handler"

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/wytnij {message.text}")

        search_transcriptions = SearchTranscriptions(self._bot.get_dispatcher()) #fixme powtórka z tego co pisałem o dispatcherze
        video_manager = VideoManager(self._bot)
        content = message.text.split()
        if len(content) != 4:
            await self.__reply_invalid_args_count(message)
            return

        episode = content[1]  # Format: S02E10
        start_time = content[2]  # Format: 20:30.11
        end_time = content[3]  # Format: 21:32.50

        if episode[0] != 'S' or 'E' not in episode:
            await self.__reply_incorrect_season_episode_format(message)
            return

        season = int(episode[1:3])
        episode_number = int(episode[4:6])

        absolute_episode_number = (season - 1) * 13 + episode_number

        video_path = await search_transcriptions.find_video_path_by_episode(season, absolute_episode_number)
        if not video_path or not os.path.exists(video_path):
            await self.__reply_video_file_not_exist(message, video_path)
            return

        start_seconds = minutes_str_to_seconds(start_time)
        end_seconds = minutes_str_to_seconds(end_time)

        if start_seconds is None or end_seconds is None:
            await self.__reply_incorrect_time_format(message)
            return

        if end_seconds <= start_seconds:
            await self.__reply_end_time_earlier_than_start(message)
            return

        await video_manager.extract_and_send_clip(message.chat.id, video_path, start_seconds, end_seconds)
        await self._log_system_message(logging.INFO, f"Clip extracted and sent for command: /manual {episode} {start_time} {end_time}")

        last_manual_clip[message.chat.id] = {
            'video_path': video_path,
            'start': start_seconds,
            'end': end_seconds,
            'episode_info': {
                'season': season,
                'episode_number': episode_number,
            },
        }

    async def __reply_invalid_args_count(self, message: Message) -> None: #fixme tak sobie myśle czy nie zrobić w klasie bazowej jakiejś metody od chujowych argumentow bo to tez czesc wspolna
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
