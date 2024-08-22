import json
from typing import List

from bot.database.database_manager import UserProfile
from bot.database.models import FormattedSegmentInfo


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


def convert_seconds_to_time_str(seconds: int) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def time_str_to_seconds(time_str: str) -> int:
    h, m, s = [int(part) for part in time_str.split(':')]
    return h * 3600 + m * 60 + s


def parse_whitelist_message(
        content: List[str],
) -> UserProfile:
    try:
        user_id = int(content[0])
    except ValueError as exc:
        raise ValueError(f"Invalid user_id: {content[0]} is not a valid integer.") from exc

    return UserProfile(
        user_id=user_id,
        username=content[1] if len(content) > 1 else None,
        full_name=content[2] if len(content) > 2 else None,
        subscription_end=None,
        note=None,
    )


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
