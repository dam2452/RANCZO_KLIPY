from dataclasses import (
    dataclass,
    field,
)
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
