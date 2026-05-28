import json
import logging
from pathlib import Path
from typing import (
    Annotated,
    Optional,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from bot.database.database_manager import DatabaseManager
from bot.platforms.rest_api_auth import (
    WorkerUser,
    require_worker_auth,
)
from bot.platforms.rest_api_responses import (
    ClipAdjustRequest,
    ClipCompileRequest,
    ClipCreateRequest,
    ClipResponse,
    DeleteResponse,
    EpisodesResponse,
    SavedClipCreateRequest,
    SavedClipItem,
    SavedClipsResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
)
from bot.platforms.rest_api_video import (
    serve_thumbnail,
    stream_video,
)
from bot.search.infra.elastic_search_manager import ElasticSearchManager
from bot.search.scenes_finder import ScenesFinder
from bot.search.semantic_segments_finder import SemanticSegmentsFinder
from bot.search.text_segments_finder import TextSegmentsFinder
from bot.settings import settings as s
from bot.utils.constants import (
    ElasticsearchKeys,
    EpisodeMetadataKeys,
    SegmentKeys,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.keyframe_extractor import KeyframeExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rest", tags=["REST Worker API"])


async def _get_active_series(user_id: int) -> str:
    series_names = await DatabaseManager.get_user_active_series_names(user_id)
    if series_names:
        return series_names[0]
    return s.DEFAULT_SERIES


def _segment_to_result(seg: dict) -> SearchResultItem:
    source = seg.get("_source", seg)
    meta = source.get(EpisodeMetadataKeys.EPISODE_METADATA, {}) or {}
    return SearchResultItem(
        id=str(source.get(SegmentKeys.SEGMENT_ID, seg.get(ElasticsearchKeys.SCORE, ""))),
        text=source.get(SegmentKeys.TEXT, ""),
        speaker=source.get("speaker"),
        start_time=source.get(SegmentKeys.START_TIME, 0),
        end_time=source.get(SegmentKeys.END_TIME, 0),
        score=seg.get(ElasticsearchKeys.SCORE),
        season=meta.get(EpisodeMetadataKeys.SEASON),
        episode=meta.get(EpisodeMetadataKeys.EPISODE_NUMBER),
        episode_title=meta.get("title"),
        video_path=source.get(SegmentKeys.VIDEO_PATH),
    )


def _resolve_video_path(video_path: str) -> Path:
    resolved = Path(s.VIDEO_DATA_DIR) / video_path
    if not resolved.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source video file not found.")
    if not str(resolved.resolve()).startswith(str(Path(s.VIDEO_DATA_DIR).resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return resolved


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    series_name = body.series or await _get_active_series(user.user_id)
    es = await ElasticSearchManager.connect_to_elasticsearch(logger)

    if body.semantic:
        segments = await SemanticSegmentsFinder.find_by_text(
            query=body.query,
            logger=logger,
            series_name=series_name,
            size=min(body.limit, s.MAX_ES_RESULTS_LONG),
        )
    else:
        segments = await ScenesFinder.find_by_text_and_filter(
            es=es,
            series_names=[series_name],
            quote=body.query,
            search_filter=None,
            size=min(body.limit, s.MAX_ES_RESULTS_LONG),
            logger=logger,
        )

    results = [_segment_to_result(seg) for seg in (segments or [])]
    return SearchResponse(results=results[: body.limit], total=len(results), query=body.query)


@router.post("/clip", response_model=ClipResponse)
async def create_clip(
    body: ClipCreateRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    duration = body.end_time - body.start_time
    if duration <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be greater than start_time.")
    if duration > s.MAX_CLIP_DURATION:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Clip duration exceeds maximum of {s.MAX_CLIP_DURATION}s.")

    series_name = body.series or await _get_active_series(user.user_id)

    es = await ElasticSearchManager.connect_to_elasticsearch(logger)
    segments = await ScenesFinder.find_by_text_and_filter(
        es=es,
        series_names=[series_name],
        quote=body.segment_id,
        search_filter=None,
        size=1,
        logger=logger,
    )

    if not segments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found.")

    source = segments[0].get("_source", segments[0])
    video_path_raw = source.get(SegmentKeys.VIDEO_PATH, "")
    if not video_path_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment has no video path.")

    video_path = _resolve_video_path(video_path_raw)

    start = max(0, body.start_time - s.EXTEND_BEFORE)
    end = body.end_time + s.EXTEND_AFTER

    output_path = await ClipsExtractor.extract_clip(video_path, start, end, logger)

    await KeyframeExtractor.extract_thumbnail_bytes(video_path, start, duration)

    segment_data = {SegmentKeys.VIDEO_PATH: video_path_raw, SegmentKeys.START_TIME: start, SegmentKeys.END_TIME: end}
    await DatabaseManager.insert_last_clip(
        chat_id=user.user_id,
        segment=segment_data,
        compiled_clip=None,
        clip_type="single",
        adjusted_start_time=start,
        adjusted_end_time=end,
        is_adjusted=False,
    )

    return ClipResponse(
        id=str(output_path),
        duration=round(end - start, 2),
        video_path=str(output_path),
        thumbnail_path=None,
        start_time=round(start, 2),
        end_time=round(end, 2),
    )


@router.post("/clip/adjust", response_model=ClipResponse)
async def adjust_clip(
    body: ClipAdjustRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    last_clip = await DatabaseManager.get_last_clip_by_chat_id(user.user_id)
    if not last_clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clip found to adjust.")

    segment = json.loads(last_clip.segment) if isinstance(last_clip.segment, str) else last_clip.segment
    video_path_raw = segment.get(SegmentKeys.VIDEO_PATH, "")
    if not video_path_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip has no video path.")

    video_path = _resolve_video_path(video_path_raw)

    current_start = last_clip.adjusted_start_time or segment.get(SegmentKeys.START_TIME, 0)
    current_end = last_clip.adjusted_end_time or segment.get(SegmentKeys.END_TIME, 0)

    if body.absolute_start is not None and body.absolute_end is not None:
        new_start = body.absolute_start
        new_end = body.absolute_end
    else:
        new_start = current_start + (body.start_adjust or 0)
        new_end = current_end + (body.end_adjust or 0)

    duration = new_end - new_start
    if duration <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adjusted duration must be positive.")
    if duration > s.MAX_CLIP_DURATION_HARD_LIMIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Adjusted clip exceeds hard limit of {s.MAX_CLIP_DURATION_HARD_LIMIT}s.")

    new_start = max(0, new_start)

    output_path = await ClipsExtractor.extract_clip(video_path, new_start, new_end, logger)

    await KeyframeExtractor.extract_thumbnail_bytes(video_path, new_start, duration)

    await DatabaseManager.insert_last_clip(
        chat_id=user.user_id,
        segment=segment,
        compiled_clip=None,
        clip_type="adjusted",
        adjusted_start_time=new_start,
        adjusted_end_time=new_end,
        is_adjusted=True,
    )

    return ClipResponse(
        id=str(output_path),
        duration=round(duration, 2),
        video_path=str(output_path),
        thumbnail_path=None,
        start_time=round(new_start, 2),
        end_time=round(new_end, 2),
    )


@router.post("/clip/compile", response_model=ClipResponse)
async def compile_clips(
    body: ClipCompileRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Clip compilation endpoint is not yet implemented in worker mode.",
    )


@router.get("/clip/{clip_id:path}/video")
async def get_clip_video(
    request: Request,
    clip_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
):
    file_path = Path(clip_id)

    resolved = file_path.resolve()
    if not resolved.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip video not found.")

    if resolved.suffix.lower() not in {".mp4", ".webm", ".mkv", ".avi"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type.")

    return stream_video(resolved, request)


@router.get("/saved-clips", response_model=SavedClipsResponse)
async def list_saved_clips(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    clips = await DatabaseManager.get_saved_clips(user.user_id)
    items = [
        SavedClipItem(
            id=c.id,
            name=c.clip_name,
            duration=c.duration,
            created_at=str(c.timestamp) if hasattr(c, "timestamp") else None,
            season=c.season,
            episode=c.episode_number,
        )
        for c in clips
    ]
    return SavedClipsResponse(clips=items)


@router.post("/saved-clips")
async def save_clip(
    body: SavedClipCreateRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    last_clip = await DatabaseManager.get_last_clip_by_chat_id(user.user_id)
    if not last_clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clip to save.")

    segment = json.loads(last_clip.segment) if isinstance(last_clip.segment, str) else last_clip.segment

    clip_path = Path(body.clip_id) if body.clip_id != "last" else None
    video_data = b""
    if clip_path and clip_path.exists():
        video_data = clip_path.read_bytes()

    start_time = last_clip.adjusted_start_time or segment.get(SegmentKeys.START_TIME, 0)
    end_time = last_clip.adjusted_end_time or segment.get(SegmentKeys.END_TIME, 0)

    await DatabaseManager.save_clip(
        chat_id=user.user_id,
        user_id=user.user_id,
        clip_name=body.name,
        video_data=video_data,
        start_time=start_time,
        end_time=end_time,
        duration=round(end_time - start_time, 2),
        is_compilation=False,
    )

    return {"saved": True, "name": body.name}


@router.delete("/saved-clips/{clip_name:path}", response_model=DeleteResponse)
async def delete_saved_clip(
    clip_name: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    await DatabaseManager.delete_clip(user.user_id, clip_name)
    return DeleteResponse(deleted=True)


@router.get("/episodes", response_model=EpisodesResponse)
async def list_episodes(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
    season: Optional[int] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)

    if season is not None:
        episodes = await TextSegmentsFinder.find_episodes_by_season(
            season=season,
            logger=logger,
            index=f"{series_name}_text_segments",
        )
        items = [
            {"season": season, "episode": ep.get("episode_number", 0), "title": ep.get("title", "")}
            for ep in (episodes or [])
        ]
    else:
        seasons = await TextSegmentsFinder.get_season_details_from_elastic(
            logger=logger,
            series_name=series_name,
        )
        items = [
            {"season": int(s), "episode": 0, "title": f"Sezon {s} ({count} odcinków)"}
            for s, count in (seasons.items() if seasons else [])
        ]

    return EpisodesResponse(episodes=items)


@router.get("/clip/{clip_id:path}/thumbnail")
async def get_clip_thumbnail(
    clip_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    clips = await DatabaseManager.get_saved_clips(user.user_id)
    for clip in clips:
        if clip.clip_name == clip_id and hasattr(clip, "thumbnail_data") and clip.thumbnail_data:
            return serve_thumbnail(clip.thumbnail_data)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found.")
