from dataclasses import (
    dataclass,
    field,
)
from io import BytesIO
from typing import (
    Optional,
    Union,
)


@dataclass
class EpisodeInfo:
    season: Optional[int] = None
    episode_number: Optional[int] = None


# fixme no z dupy troche: 1) serio mozesz miec wszystko None? 2) Uzywasz w projekcie jednoczesnie BytesIO i zwyklych bytes?
@dataclass
class SegmentInfo:
    video_path: Optional[str] = None
    start: Optional[int] = 0
    end: Optional[int] = 0
    episode_info: EpisodeInfo = field(default_factory=EpisodeInfo)
    compiled_clip: Optional[Union[bytes, BytesIO]] = None
    expanded_clip: Optional[Union[bytes, BytesIO]] = None
    expanded_start: Optional[int] = 0
    expanded_end: Optional[int] = 0
