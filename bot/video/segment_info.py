from dataclasses import (
    dataclass,
    field,
)
import json
from typing import Optional


@dataclass
class EpisodeInfo:
    season: Optional[int] = None
    episode_number: Optional[int] = None


@dataclass
class SegmentInfo:
    video_path: Optional[str] = None
    start: int = 0
    end: int = 0
    episode_info: EpisodeInfo = field(default_factory=EpisodeInfo)
    compiled_clip: Optional[bytes] = None
    expanded_clip: Optional[bytes] = None
    expanded_start: int = 0
    expanded_end: int = 0


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
