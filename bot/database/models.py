from dataclasses import dataclass
from datetime import (
    date,
    datetime,
)
from enum import Enum
from typing import (
    List,
    Optional,
)


@dataclass
class UserProfile:
    user_id: int
    username: Optional[str]
    full_name: Optional[str]
    subscription_end: Optional[date]
    note: Optional[str]


@dataclass
class UserRole:
    user_id: int
    is_admin: bool
    is_moderator: bool


@dataclass
class VideoClip:
    id: int
    chat_id: int
    user_id: int
    clip_name: str
    video_data: bytes
    start_time: float
    end_time: float
    duration: float
    season: Optional[int]
    episode_number: Optional[int]
    is_compilation: bool


class ClipType(Enum):
    MANUAL = "manual"
    COMPILED = "compiled"
    SELECTED = "selected"
    ADJUSTED = "adjusted"
    SINGLE = "single"


@dataclass
class LastClip:
    id: int
    chat_id: int
    segment: dict
    compiled_clip: Optional[bytes]
    clip_type: Optional[ClipType]
    adjusted_start_time: Optional[float]
    adjusted_end_time: Optional[float]
    is_adjusted: bool
    timestamp: date


@dataclass
class SearchHistory:
    id: int
    chat_id: int
    quote: str
    segments: str


@dataclass(frozen=True)
class FormattedSegmentInfo:
    episode_formatted: str
    time_formatted: str
    episode_title: str


@dataclass
class EpisodeInfo:
    season: Optional[int] = None
    episode_number: Optional[int] = None
    title: Optional[str] = None


@dataclass
class SegmentInfo:
    video_path: str
    start: float
    end: float
    episode_info: EpisodeInfo
    text: Optional[str] = None
    id: Optional[int] = None
    author: Optional[str] = None
    comment: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    actors: Optional[List[str]] = None
    compiled_clip: Optional[bytes] = None


@dataclass
class UserMessage:
    user_id: int
    key: str
    timestamp: Optional[datetime] = None
