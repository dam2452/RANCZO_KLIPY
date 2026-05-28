from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)


class SearchMode(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC_TEXT = "semantic_text"
    SEMANTIC_FRAMES = "semantic_frames"
    SEMANTIC_EPISODE = "semantic_episode"


class EpisodeSpec(BaseModel):
    season: Optional[int] = None
    episode: int


class ObjectFilterSpec(BaseModel):
    name: str
    operator: Optional[str] = None
    value: Optional[int] = None


class SearchFilters(BaseModel):
    seasons: Optional[list[int]] = None
    episodes: Optional[list[EpisodeSpec]] = None
    episode_title: Optional[str] = None
    characters: Optional[list[str]] = None
    emotions: Optional[list[str]] = None
    objects: Optional[list[ObjectFilterSpec]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    mode: SearchMode = SearchMode.KEYWORD
    series: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    filters: Optional[SearchFilters] = None


class CharacterSearchRequest(BaseModel):
    character: str = Field(..., min_length=1, max_length=100)
    emotion: Optional[str] = None
    series: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    filters: Optional[SearchFilters] = None


class ObjectSearchRequest(BaseModel):
    object: str = Field(..., min_length=1, max_length=100)
    quantity_filter: Optional[ObjectFilterSpec] = None
    series: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    filters: Optional[SearchFilters] = None


class TranscriptRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    context_size: int = Field(30, ge=5, le=100)
    series: Optional[str] = None


class ClipCreateRequest(BaseModel):
    segment_id: str = Field(..., min_length=1, max_length=256)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    series: Optional[str] = None


class ClipCutRequest(BaseModel):
    season: int = Field(..., ge=0)
    episode: int = Field(..., ge=1)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    series: Optional[str] = None


class ClipAdjustRequest(BaseModel):
    clip_id: str = Field(..., min_length=1, max_length=256)
    start_adjust: Optional[float] = Field(None, ge=-300, le=300)
    end_adjust: Optional[float] = Field(None, ge=-300, le=300)
    absolute_start: Optional[float] = Field(None, ge=0)
    absolute_end: Optional[float] = Field(None, gt=0)


class ClipSnapRequest(BaseModel):
    clip_id: str = "last"


class ClipCompileSegment(BaseModel):
    video_path: str = Field(..., min_length=1, max_length=512)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)


class ClipCompileRequest(BaseModel):
    segments: list[ClipCompileSegment] = Field(..., min_length=2, max_length=30)
    series: Optional[str] = None


class SearchResultItem(BaseModel):
    id: str
    text: Optional[str] = None
    speaker: Optional[str] = None
    start_time: float
    end_time: float
    score: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    video_path: Optional[str] = None


class CharacterSearchResultItem(BaseModel):
    id: str
    character: str
    emotion: Optional[str] = None
    start_time: float
    end_time: float
    score: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    video_path: Optional[str] = None


class ObjectSearchResultItem(BaseModel):
    id: str
    object_name: str
    count: Optional[int] = None
    start_time: float
    end_time: float
    score: Optional[float] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    video_path: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int
    query: str


class CharacterSearchResponse(BaseModel):
    results: list[CharacterSearchResultItem]
    total: int
    character: str
    emotion: Optional[str] = None


class ObjectSearchResponse(BaseModel):
    results: list[ObjectSearchResultItem]
    total: int
    object_name: str


class ClipResponse(BaseModel):
    id: str
    duration: float
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    start_time: float
    end_time: float


class ClipSnapResponse(BaseModel):
    snapped: bool
    message: Optional[str] = None
    clip: Optional[ClipResponse] = None


class CharacterItem(BaseModel):
    name: str
    episode_count: int


class ObjectItem(BaseModel):
    name: str
    scene_count: int


class SeasonItem(BaseModel):
    season: int
    episode_count: int


class EpisodeDetail(BaseModel):
    episode_number: int
    title: str


class TranscriptLine(BaseModel):
    time: str
    speaker: Optional[str] = None
    text: str


class TranscriptResponse(BaseModel):
    segment_id: str
    text: str
    speaker: Optional[str] = None
    start_time: float
    end_time: float
    surrounding: list[TranscriptLine] = []


class DeleteResponse(BaseModel):
    deleted: bool
