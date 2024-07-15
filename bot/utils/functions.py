from dataclasses import dataclass
import json
import tempfile
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram import Bot
from aiogram.types import FSInputFile

from bot.utils.database import DatabaseManager
from bot.utils.global_dicts import last_clip
from bot.utils.video_manager import VideoManager


@dataclass(frozen=True)
class FormattedSegmentInfo:
    episode_formatted: str
    time_formatted: str
    episode_title: str


def format_segment(segment: json) -> FormattedSegmentInfo:
    episode_info = segment.get('episode_info', {})
    total_episode_number = episode_info.get('episode_number', 'Unknown')
    season_number = (total_episode_number - 1) // 13 + 1 if isinstance(total_episode_number, int) else 'Unknown'
    episode_number_in_season = (total_episode_number - 1) % 13 + 1 if isinstance(
        total_episode_number,
        int,
    ) else 'Unknown'

    season = str(season_number).zfill(2)
    episode_number = str(episode_number_in_season).zfill(2)

    start_time = int(segment['start'])
    minutes, seconds = divmod(start_time, 60)

    return FormattedSegmentInfo(
        episode_formatted=f"S{season}E{episode_number}",
        time_formatted=f"{minutes:02}:{seconds:02}",
        episode_title=episode_info.get('title', 'Unknown'),
    )


async def compile_clips(selected_clips_data: List[bytes]) -> str:
    temp_files = []
    for video_data in selected_clips_data:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")  # pylint: disable=consider-using-with
        temp_files.append(temp_file.name)
        with open(temp_file.name, 'wb') as f:
            f.write(video_data)

    compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")  # pylint: disable=consider-using-with
    compiled_output.close()

    await VideoManager.concatenate_clips(temp_files, compiled_output.name)

    return compiled_output.name


async def send_compiled_clip(chat_id: int, compiled_output: str, bot: Bot) -> None:
    with open(compiled_output, 'rb') as f:
        compiled_clip_data = f.read()

    last_clip[chat_id] = {
        'compiled_clip': compiled_clip_data,
        'type': 'compiled',
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


def minutes_str_to_seconds(time_str: str) -> float:
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


def parse_whitelist_message(content: List[str], default_admin_status: Optional[bool],
                            default_moderator_status: Optional[bool]) -> DatabaseManager.User:
    return DatabaseManager.User(
        name=content[1],
        is_admin=bool(int(content[2])) if len(content) > 2 else default_admin_status,
        is_moderator=bool(int(content[3])) if len(content) > 3 else default_moderator_status,
        full_name=content[4] if len(content) > 4 else None,
        email=content[5] if len(content) > 5 else None,
        phone=content[6] if len(content) > 6 else None,
    )
