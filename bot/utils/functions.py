import tempfile
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram import Bot
from aiogram.types import FSInputFile

from bot.utils.global_dicts import last_compiled_clip
from bot.utils.video_manager import VideoManager


async def compile_clips(selected_clips_data: List[bytes], bot: Bot) -> str:
    temp_files = []
    for video_data in selected_clips_data:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_files.append(temp_file.name)
        with open(temp_file.name, 'wb') as f:
            f.write(video_data)

    compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    compiled_output.close()

    await VideoManager.concatenate_clips(temp_files, compiled_output.name, bot)

    return compiled_output.name


async def send_compiled_clip(chat_id: int, compiled_output: str, bot: Bot) -> None:
    with open(compiled_output, 'rb') as f:
        compiled_clip_data = f.read()

    last_compiled_clip[chat_id] = {
        'compiled_clip': compiled_clip_data,
        'is_compilation': True,
    }

    await bot.send_video(chat_id, FSInputFile(compiled_output), supports_streaming=True, width=1920, height=1080)


def adjust_episode_number(absolute_episode: int) -> Optional[Tuple[int, int]]:
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode


class InvalidTimeStringException(Exception):
    def __init__(self, time: str) -> None:
        self.message = f"Invalid time string: '{time}'"
        super().__init__(self.message)


def minutes_str_to_seconds(
        time_str: str,
) -> float:
    try:
        minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    except (TypeError, ValueError) as e:
        raise InvalidTimeStringException from e


class InvalidSeasonEpisodeStringException(Exception):
    def __init__(self, episode_string: str):
        self.message = f"Invalid season episode string '{episode_string}'"
        super().__init__(self.message)


class Episode:
    EPISODES_PER_SEASON: int = 13

    def __init__(self, season_episode: str) -> None:
        if season_episode[0] != "S" or season_episode[3] != "E":
            raise InvalidSeasonEpisodeStringException(season_episode)

        self.season: int = int(season_episode[1:3])
        self.number: int = int(season_episode[4:6])

    def get_absolute_episode_number(self) -> int:
        return (self.season - 1) * Episode.EPISODES_PER_SEASON + self.number
