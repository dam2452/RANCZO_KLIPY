from dataclasses import dataclass
import json
from typing import (
    List,
    Optional,
)

from aiogram import Bot
from aiogram.types import Message

from bot.settings import Settings
from bot.utils.database import DatabaseManager
from bot.utils.video_manager import VideoManager


async def extract_and_send_clip(
    segment: json, message: Message, bot: Bot, extend_before: int = Settings.EXTEND_BEFORE,
    extend_after: int = Settings.EXTEND_AFTER,
) -> None:
    video_path = segment['video_path']
    start_time = max(0, segment['start'] - extend_before)
    end_time = segment['end'] + extend_after
    await VideoManager.extract_and_send_clip(message.chat.id, video_path, start_time, end_time, bot)


@dataclass(frozen=True)
class FormattedSegmentInfo:
    episode_formatted: str
    time_formatted: str
    episode_title: str


def format_segment(segment: json, episodes_per_season: int = 13) -> FormattedSegmentInfo:
    episode_info = segment.get('episode_info', {})
    total_episode_number = episode_info.get('episode_number', 'Unknown')
    season_number = (total_episode_number - 1) // episodes_per_season + 1 if isinstance(total_episode_number, int) else 'Unknown'
    episode_number_in_season = (total_episode_number - 1) % episodes_per_season + 1 if isinstance(total_episode_number, int) else 'Unknown'

    season = str(season_number).zfill(2)
    episode_number = str(episode_number_in_season).zfill(2)

    start_time = int(segment['start'])
    minutes, seconds = divmod(start_time, 60)

    return FormattedSegmentInfo(
        episode_formatted=f"S{season}E{episode_number}",
        time_formatted=f"{minutes:02}:{seconds:02}",
        episode_title=episode_info.get('title', 'Unknown'),
    )


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


def parse_whitelist_message(
        content: List[str], default_admin_status: Optional[bool],
        default_moderator_status: Optional[bool],
) -> DatabaseManager.User:
    return DatabaseManager.User(
        name=content[1],
        is_admin=bool(int(content[2])) if len(content) > 2 else default_admin_status,
        is_moderator=bool(int(content[3])) if len(content) > 3 else default_moderator_status,
        full_name=content[4] if len(content) > 4 else None,
        email=content[5] if len(content) > 5 else None,
        phone=content[6] if len(content) > 6 else None,
    )
