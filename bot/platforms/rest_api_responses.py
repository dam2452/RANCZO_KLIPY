from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    semantic: bool = False
    series: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)


class ClipCreateRequest(BaseModel):
    segment_id: str = Field(..., min_length=1, max_length=256)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    series: Optional[str] = None


class ClipAdjustRequest(BaseModel):
    clip_id: str = Field(..., min_length=1, max_length=256)
    start_adjust: Optional[float] = Field(None, ge=-300, le=300)
    end_adjust: Optional[float] = Field(None, ge=-300, le=300)
    absolute_start: Optional[float] = Field(None, ge=0)
    absolute_end: Optional[float] = Field(None, gt=0)


class ClipCompileSegment(BaseModel):
    segment_id: str = Field(..., min_length=1, max_length=256)
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)


class ClipCompileRequest(BaseModel):
    clips: list[ClipCompileSegment] = Field(..., min_length=2, max_length=30)
    name: Optional[str] = Field(None, min_length=1, max_length=40)


class SavedClipCreateRequest(BaseModel):
    clip_id: str = Field(..., min_length=1, max_length=256)
    name: str = Field(..., min_length=1, max_length=40)
    tags: list[str] = Field(default_factory=list, max_length=10)


class SearchResultItem(BaseModel):
    id: str
    text: str
    speaker: Optional[str] = None
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


class ClipResponse(BaseModel):
    id: str
    duration: float
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    start_time: float
    end_time: float


class SavedClipItem(BaseModel):
    id: int
    name: str
    duration: Optional[float] = None
    created_at: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None


class SavedClipsResponse(BaseModel):
    clips: list[SavedClipItem]


class EpisodeItem(BaseModel):
    season: int
    episode: int
    title: str


class EpisodesResponse(BaseModel):
    episodes: list[EpisodeItem]


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


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
