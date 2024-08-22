from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


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
    MANUAL = 'manual'
    COMPILED = 'compiled'
    SELECTED = 'selected'
    ADJUSTED = 'adjusted'
    SINGLE = 'single'


@dataclass
class LastClip:
    id: int
    chat_id: int
    segment: str
    compiled_clip: Optional[bytes]
    clip_type: Optional[ClipType]
    adjusted_start_time: Optional[float]
    adjusted_end_time: Optional[float]
    is_adjusted: bool
    timestamp: date


@dataclass  #fixme użyć
class UserMessage:
    id: int
    user_id: int
    message_content: str
    timestamp: date


@dataclass
class SearchHistory:
    id: int
    chat_id: int
    quote: str
    segments: str
