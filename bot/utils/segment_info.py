from io import BytesIO
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Optional,
    Union,
    Dict,
)


@dataclass
class EpisodeInfo:
    season: Optional[int] = None
    episode_number: Optional[int] = None


@dataclass
class SegmentInfo:
    video_path: Optional[str] = None
    start: Optional[int] = 0
    end: Optional[int] = 0
    episode_info: EpisodeInfo = field(default_factory=EpisodeInfo)
    compiled_clip: Optional[Union[bytes, 'BytesIO']] = None
    expanded_clip: Optional[Union[bytes, 'BytesIO']] = None
    expanded_start: Optional[int] = 0
    expanded_end: Optional[int] = 0
