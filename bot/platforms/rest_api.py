import asyncio
import json
import logging
import os
from pathlib import Path
import tempfile
from typing import (
    Annotated,
    Dict,
    Optional,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.integrations.s3_client import S3Client
from bot.platforms.rest_api_auth import (
    WorkerUser,
    require_worker_auth,
)
from bot.platforms.rest_api_responses import (
    CharacterItem,
    ClipAdjustRequest,
    ClipCompileRequest,
    ClipCreateRequest,
    ClipCutRequest,
    ClipResponse,
    ClipSnapRequest,
    ClipSnapResponse,
    ClipSubtitlesRequest,
    ClipSubtitlesResponse,
    EmotionItem,
    EpisodeDetail,
    IndexStatsResponse,
    ObjectItem,
    ReindexRequest,
    ReindexResponse,
    ReindexStatusResponse,
    SearchFilters,
    SearchMode,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SeasonItem,
    SubtitleLine,
    TranscriptRequest,
    TranscriptResponse,
)
from bot.platforms.rest_api_video import _build_streaming_response
from bot.search.filter_applicator import FilterApplicator
from bot.search.infra.elastic_search_manager import ElasticSearchManager
from bot.search.scenes_finder import ScenesFinder
from bot.search.semantic_segments_finder import (
    SemanticSearchMode,
    SemanticSegmentsFinder,
)
from bot.search.text_segments_finder import TextSegmentsFinder
from bot.search.video_frames.character_finder import CharacterFinder
from bot.search.video_frames.object_finder import ObjectFinder
from bot.services.reindex.reindex_service import ReindexService
from bot.services.reindex.reindex_task_manager import task_manager
from bot.services.scene_snap.scene_snap_service import SceneSnapService
from bot.settings import settings as s
from bot.utils.constants import (
    ElasticsearchKeys,
    EpisodeMetadataKeys,
    SegmentKeys,
)
from bot.video.audio_extractor import (
    SUPPORTED_AUDIO_FORMATS,
    AudioExtractor,
)
from bot.video.clips_extractor import ClipsExtractor
from bot.video.file_streaming import (
    build_full_response,
    build_range_response,
)
from bot.video.keyframe_extractor import KeyframeExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rest", tags=["REST Worker API"])


async def _get_active_series(user_id: int) -> str:
    if s.INTERNAL_MODE:
        return s.DEFAULT_SERIES
    series_names = await DatabaseManager.get_user_active_series_names(user_id)
    if series_names:
        return series_names[0]
    return s.DEFAULT_SERIES


def _to_internal_filter(filters: Optional[SearchFilters]) -> Optional[dict]:
    if not filters:
        return None
    sf = {}
    if filters.seasons:
        sf["seasons"] = filters.seasons
    if filters.episodes:
        sf["episodes"] = [{"season": e.season, "episode": e.episode} for e in filters.episodes]
    if filters.episode_title:
        sf["episode_title"] = filters.episode_title
    if filters.characters:
        sf["character_groups"] = [filters.characters]
    if filters.emotions:
        sf["emotions"] = filters.emotions
    if filters.objects:
        sf["object_groups"] = [
            [{"name": o.name, "operator": o.operator, "value": o.value} for o in filters.objects],
        ]
    return sf if sf else None


def _segment_to_result(seg: dict) -> SearchResultItem:
    source = seg.get("_source", seg)
    meta = source.get(EpisodeMetadataKeys.EPISODE_METADATA, {}) or {}
    scene_timestamps = source.get("scene_timestamps") or {}
    episode_duration = (scene_timestamps.get("video_info") or {}).get("duration")
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
        episode_duration=episode_duration,
    )


async def _resolve_video_path(video_path: str) -> Path:
    if s.STORAGE_BACKEND == "s3":
        s3_client = S3Client()
        temp_path = await s3_client.download_to_temp(video_path)
        return temp_path

    resolved = Path(s.VIDEO_DATA_DIR) / video_path
    if not resolved.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source video file not found.")
    if not str(resolved.resolve()).startswith(str(Path(s.VIDEO_DATA_DIR).resolve())):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return resolved


def _validate_tmp_path(file_path: Path) -> Path:
    if not file_path.is_absolute():
        file_path = Path("/") / file_path
    resolved = file_path.resolve()
    if not resolved.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    if resolved.suffix.lower() not in {".mp4", ".webm", ".mkv", ".avi", ".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type.")
    if not str(resolved).startswith("/tmp/"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return resolved



@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/stats", response_model=IndexStatsResponse)
async def get_index_stats(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)
    stats = await TextSegmentsFinder.get_index_stats(logger, series_name)
    return IndexStatsResponse(
        total_segments=stats["total_segments"],
        total_episodes=stats["total_episodes"],
        total_seasons=stats["total_seasons"],
        total_hours=stats["total_hours"],
        series=[series_name],
    )


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    series_name = body.series or await _get_active_series(user.user_id)
    search_filter = _to_internal_filter(body.filters)
    has_query = bool(body.query and body.query.strip())

    if not has_query and search_filter:
        has_frame_filters = bool(
            search_filter.get("character_groups")
            or search_filter.get("emotions")
            or search_filter.get("object_groups"),
        )
        if has_frame_filters:
            episode_keys = await FilterApplicator.collect_eligible_episodes(search_filter, series_name, logger)
            if episode_keys:
                all_segments = await TextSegmentsFinder.find_segments_by_filter_only(
                    logger=logger,
                    series_name=series_name,
                    search_filter=search_filter,
                    size=s.MAX_ES_RESULTS_LONG,
                    restrict_episode_keys=episode_keys,
                )
                segments = await FilterApplicator.apply_to_text_segments(
                    all_segments, search_filter, series_name, logger,
                )
            else:
                segments = []
        else:
            es = await ElasticSearchManager.connect_to_elasticsearch(logger)
            segments = await ScenesFinder.find_by_filter(
                es=es,
                series_names=[series_name],
                search_filter=search_filter,
                size=min(body.limit, s.MAX_ES_RESULTS_LONG),
                logger=logger,
            )
    elif body.mode == SearchMode.KEYWORD:
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        segments = await ScenesFinder.find_by_text_and_filter(
            es=es,
            series_names=[series_name],
            quote=body.query,
            search_filter=search_filter,
            size=min(body.limit, s.MAX_ES_RESULTS_LONG),
            logger=logger,
        )
    elif body.mode in (SearchMode.SEMANTIC_TEXT, SearchMode.SEMANTIC_FRAMES, SearchMode.SEMANTIC_EPISODE):
        mode_map = {
            SearchMode.SEMANTIC_TEXT: SemanticSearchMode.TEXT,
            SearchMode.SEMANTIC_FRAMES: SemanticSearchMode.FRAMES,
            SearchMode.SEMANTIC_EPISODE: SemanticSearchMode.EPISODE,
        }
        segments = await SemanticSegmentsFinder.find_by_text(
            query=body.query,
            logger=logger,
            series_name=series_name,
            mode=mode_map[body.mode],
            size=min(body.limit, s.MAX_ES_RESULTS_LONG),
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search mode.")

    results = [_segment_to_result(seg) for seg in (segments or [])]
    return SearchResponse(results=results[: body.limit], total=len(results), query=body.query or "")


@router.post("/transcript", response_model=TranscriptResponse)
async def get_transcript(
    body: TranscriptRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    series_name = body.series or await _get_active_series(user.user_id)

    result = await TextSegmentsFinder.find_segment_with_context(
        quote=body.query,
        logger=logger,
        series_name=series_name,
        context_size=body.context_size,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found.")

    target = result.get("target", result)
    context_lines = result.get("context", [])
    surrounding_lines = [
        {"time": str(line.get("start", "")), "speaker": line.get("speaker"), "text": line.get("text", "")}
        for line in context_lines
    ]

    return TranscriptResponse(
        segment_id=str(target.get("segment_id", target.get("id", ""))),
        text=target.get("text", ""),
        speaker=target.get("speaker"),
        start_time=target.get("start_time", target.get("start", 0)),
        end_time=target.get("end_time", target.get("end", 0)),
        surrounding=surrounding_lines,
    )


@router.post("/clip-subtitles", response_model=ClipSubtitlesResponse)
async def get_clip_subtitles(
    body: ClipSubtitlesRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    series_name = body.series or await _get_active_series(user.user_id)

    if body.video_path:
        video_path = body.video_path
    else:
        video_path = await TextSegmentsFinder.find_video_path_by_episode(
            season=body.season,
            episode_number=body.episode,
            logger=logger,
            index=f"{series_name}_text_segments",
        )
        if not video_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode video not found.")

    segments = await TextSegmentsFinder.find_segments_in_time_range(
        video_path=video_path,
        start_time=body.start_time,
        end_time=body.end_time,
        logger=logger,
        series_name=series_name,
    )
    lines = [
        SubtitleLine(
            start_time=seg.get(SegmentKeys.START_TIME, seg.get("start", 0.0)),
            end_time=seg.get(SegmentKeys.END_TIME, seg.get("end", 0.0)),
            speaker=seg.get("speaker"),
            text=seg.get(SegmentKeys.TEXT, ""),
        )
        for seg in segments
    ]
    return ClipSubtitlesResponse(lines=lines)


@router.get("/catalogue/characters")
async def list_characters(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)
    characters = await CharacterFinder.get_all_characters(series_name, logger)
    return {
        "characters": [
            CharacterItem(name=c.get("name", ""), episode_count=c.get("episode_count", 0))
            for c in (characters or [])
        ],
    }


@router.get("/catalogue/objects")
async def list_objects(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)
    objects = await ObjectFinder.get_all_objects(series_name, logger)
    return {
        "objects": [
            ObjectItem(name=o.get("class_name", ""), scene_count=o.get("scene_count", 0))
            for o in (objects or [])
        ],
    }


@router.get("/catalogue/emotions")
async def list_emotions(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)
    emotions = await CharacterFinder.get_all_emotions(series_name, logger)
    return {
        "emotions": [
            EmotionItem(label=e.get("label", ""), count=e.get("count", 0))
            for e in (emotions or [])
        ],
    }


@router.get("/catalogue/seasons")
async def list_seasons(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
    series: Optional[str] = Query(None),
):
    series_name = series or await _get_active_series(user.user_id)
    seasons = await TextSegmentsFinder.get_season_details_from_elastic(
        logger=logger,
        series_name=series_name,
    )
    return {
        "seasons": [
            SeasonItem(season=int(s), episode_count=count)
            for s, count in (seasons.items() if seasons else [])
        ],
    }


@router.get("/catalogue/episodes")
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
        return {
            "episodes": [
                EpisodeDetail(
                    episode_number=ep.get("episode_number", 0),
                    title=ep.get("title", ""),
                    video_path=ep.get("video_path"),
                    duration=ep.get("duration"),
                )
                for ep in (episodes or [])
            ],
        }

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="season parameter is required.")


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

    video_path = await _resolve_video_path(video_path_raw)

    start = max(0, body.start_time - s.EXTEND_BEFORE)
    end = body.end_time + s.EXTEND_AFTER

    output_path = await ClipsExtractor.extract_clip(video_path, start, end, logger)

    segment_data = {SegmentKeys.VIDEO_PATH: video_path_raw, SegmentKeys.START_TIME: start, SegmentKeys.END_TIME: end}
    if not s.INTERNAL_MODE:
        await DatabaseManager.insert_last_clip(
            chat_id=user.user_id,
            segment=segment_data,
            compiled_clip=None,
            clip_type=ClipType.SINGLE,
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


@router.post("/clip/cut", response_model=ClipResponse)
async def cut_clip(
    body: ClipCutRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    duration = body.end_time - body.start_time
    if duration <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be greater than start_time.")
    if duration > s.MAX_CLIP_DURATION_HARD_LIMIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Clip duration exceeds hard limit of {s.MAX_CLIP_DURATION_HARD_LIMIT}s.")

    series_name = body.series or await _get_active_series(user.user_id)

    video_path_raw = await TextSegmentsFinder.find_video_path_by_episode(
        season=body.season,
        episode_number=body.episode,
        logger=logger,
        index=f"{series_name}_text_segments",
    )
    if not video_path_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode video not found.")

    video_path = await _resolve_video_path(video_path_raw)

    start = max(0, body.start_time - s.EXTEND_BEFORE)
    end = body.end_time + s.EXTEND_AFTER

    output_path = await ClipsExtractor.extract_clip(video_path, start, end, logger)

    segment_data = {
        SegmentKeys.VIDEO_PATH: video_path_raw,
        SegmentKeys.START_TIME: start,
        SegmentKeys.END_TIME: end,
        EpisodeMetadataKeys.EPISODE_METADATA: {
            EpisodeMetadataKeys.SEASON: body.season,
            EpisodeMetadataKeys.EPISODE_NUMBER: body.episode,
        },
    }
    if not s.INTERNAL_MODE:
        await DatabaseManager.insert_last_clip(
            chat_id=user.user_id,
            segment=segment_data,
            compiled_clip=None,
            clip_type=ClipType.MANUAL,
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
    if s.INTERNAL_MODE:
        if not body.clip_context:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="clip_context required in INTERNAL_MODE.")
        video_path_raw = body.clip_context.video_path
        current_start = body.clip_context.start_time
        current_end = body.clip_context.end_time
        segment = {SegmentKeys.VIDEO_PATH: video_path_raw, SegmentKeys.START_TIME: current_start, SegmentKeys.END_TIME: current_end}
    else:
        last_clip = await DatabaseManager.get_last_clip_by_chat_id(user.user_id)
        if not last_clip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clip found to adjust.")
        segment = json.loads(last_clip.segment) if isinstance(last_clip.segment, str) else last_clip.segment
        video_path_raw = segment.get(SegmentKeys.VIDEO_PATH, "")
        current_start = last_clip.adjusted_start_time or segment.get(SegmentKeys.START_TIME, 0)
        current_end = last_clip.adjusted_end_time or segment.get(SegmentKeys.END_TIME, 0)

    if not video_path_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip has no video path.")

    video_path = await _resolve_video_path(video_path_raw)

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

    if not s.INTERNAL_MODE:
        await DatabaseManager.insert_last_clip(
            chat_id=user.user_id,
            segment=segment,
            compiled_clip=None,
            clip_type=ClipType.ADJUSTED,
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


@router.post("/clip/snap", response_model=ClipSnapResponse)
async def snap_clip(
    body: ClipSnapRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    if s.INTERNAL_MODE:
        if not body.clip_context or not body.episode_metadata:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="clip_context and episode_metadata required in INTERNAL_MODE.")
        video_path_raw = body.clip_context.video_path
        current_start = body.clip_context.start_time
        current_end = body.clip_context.end_time
        segment = {SegmentKeys.VIDEO_PATH: video_path_raw, SegmentKeys.START_TIME: current_start, SegmentKeys.END_TIME: current_end}
        meta = body.episode_metadata
    else:
        last_clip = await DatabaseManager.get_last_clip_by_chat_id(user.user_id)
        if not last_clip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No clip found to snap.")
        segment = json.loads(last_clip.segment) if isinstance(last_clip.segment, str) else last_clip.segment
        video_path_raw = segment.get(SegmentKeys.VIDEO_PATH, "")
        current_start = last_clip.adjusted_start_time or segment.get(SegmentKeys.START_TIME, 0)
        current_end = last_clip.adjusted_end_time or segment.get(SegmentKeys.END_TIME, 0)
        meta = json.loads(last_clip.segment).get("episode_metadata", {}) if isinstance(last_clip.segment, str) else segment.get("episode_metadata", {})

    if not video_path_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip has no video path.")

    series_name = await _get_active_series(user.user_id)
    season = meta.get("season") if isinstance(meta, dict) else None
    episode = meta.get("episode_number") if isinstance(meta, dict) else None

    if season is None or episode is None:
        return ClipSnapResponse(snapped=False, message="Cannot determine episode for scene snap.")

    snapped_start, snapped_end = await SceneSnapService.snap_clip_times(
        series_name=series_name,
        segment=segment,
        clip_start=current_start,
        clip_end=current_end,
        logger=logger,
    )

    if snapped_start == current_start and snapped_end == current_end:
        return ClipSnapResponse(snapped=False, message="Clip already aligned to scene boundaries.")

    video_path = await _resolve_video_path(video_path_raw)
    output_path = await ClipsExtractor.extract_clip(video_path, snapped_start, snapped_end, logger)

    segment_data = {SegmentKeys.VIDEO_PATH: video_path_raw, SegmentKeys.START_TIME: snapped_start, SegmentKeys.END_TIME: snapped_end}
    if not s.INTERNAL_MODE:
        await DatabaseManager.insert_last_clip(
            chat_id=user.user_id,
            segment=segment_data,
            compiled_clip=None,
            clip_type=ClipType.ADJUSTED,
            adjusted_start_time=snapped_start,
            adjusted_end_time=snapped_end,
            is_adjusted=True,
        )

    clip_resp = ClipResponse(
        id=str(output_path),
        duration=round(snapped_end - snapped_start, 2),
        video_path=str(output_path),
        thumbnail_path=None,
        start_time=round(snapped_start, 2),
        end_time=round(snapped_end, 2),
    )
    return ClipSnapResponse(snapped=True, clip=clip_resp)


async def _resolve_segment(seg, series_name):
    vp_raw = seg.video_path
    if vp_raw:
        video_path = await _resolve_video_path(vp_raw)
    else:
        vp_raw = await TextSegmentsFinder.find_video_path_by_episode(
            season=seg.season,
            episode_number=seg.episode,
            logger=logger,
            index=f"{series_name}_text_segments",
        )
        if not vp_raw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode not found: s{seg.season}e{seg.episode}",
            )
        video_path = await _resolve_video_path(vp_raw)
    start = max(0.0, seg.start_time)
    end = seg.end_time
    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time range: {start}-{end}",
        )
    return video_path, start, end, vp_raw


async def _concat_clips(temp_files, compiled_output):
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as cf:
        concat_path = Path(cf.name)
    try:
        with concat_path.open("w", encoding="utf-8") as f:
            for tmp_file in temp_files:
                f.write(f"file '{tmp_file.as_posix()}'\n")
        command = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-c", "copy", "-movflags", "+faststart", "-fflags", "+genpts",
            "-avoid_negative_ts", "1", str(compiled_output),
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"FFmpeg compilation failed: {stderr.decode()}",
            )
    finally:
        concat_path.unlink(missing_ok=True)


@router.post("/clip/compile", response_model=ClipResponse)
async def compile_clips(
    body: ClipCompileRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],
):
    series_name = body.series or await _get_active_series(user.user_id)
    resolved = [await _resolve_segment(seg, series_name) for seg in body.segments]

    temp_files = []
    try:
        for vp, start, end, _ in resolved:
            temp_files.append(await ClipsExtractor.extract_clip(vp, start, end, logger))

        fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)
        compiled_output = Path(tmp_path)

        await _concat_clips(temp_files, compiled_output)

        duration = sum(end - start for _, start, end, _ in resolved)
        if not s.INTERNAL_MODE:
            await DatabaseManager.insert_last_clip(
                chat_id=user.user_id,
                segment={
                    SegmentKeys.VIDEO_PATH: resolved[0][3],
                    SegmentKeys.START_TIME: resolved[0][1],
                    SegmentKeys.END_TIME: resolved[-1][2],
                },
                compiled_clip=None,
                clip_type=ClipType.COMPILED,
                adjusted_start_time=None,
                adjusted_end_time=None,
                is_adjusted=False,
            )

        return ClipResponse(
            id=str(compiled_output),
            duration=round(duration, 2),
            video_path=str(compiled_output),
            thumbnail_path=None,
            start_time=round(resolved[0][1], 2),
            end_time=round(resolved[-1][2], 2),
        )
    finally:
        for tmp_file in temp_files:
            try:
                if tmp_file.exists():
                    tmp_file.unlink(missing_ok=True)
            except OSError:
                pass


@router.get("/clip/{clip_id:path}/video")
async def get_clip_video(
    request: Request,
    clip_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
):
    file_path = Path(clip_id)
    resolved = _validate_tmp_path(file_path)
    file_size = resolved.stat().st_size
    range_header = request.headers.get("range")

    if range_header and range_header.startswith("bytes="):
        range_spec = range_header[6:]
        parts = range_spec.split("-", 1)
        start = int(parts[0]) if parts[0] else max(0, file_size - int(parts[1]))
        end = int(parts[1]) if parts[1] else file_size - 1
        return build_range_response(resolved, start, end, file_size)

    return build_full_response(resolved, file_size)


_AUDIO_MIME: Dict[str, str] = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
}


@router.get("/clip/{clip_id:path}/audio")
async def get_clip_audio(
    clip_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
    audio_format: Annotated[str, Query(alias="format")] = "mp3",
):
    if audio_format not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{audio_format}'. Supported: {SUPPORTED_AUDIO_FORMATS}",
        )

    file_path = Path(clip_id)
    resolved = _validate_tmp_path(file_path)

    if resolved.suffix.lower() not in {".mp4", ".webm", ".mkv", ".avi"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video file type.")

    audio_path = await AudioExtractor.extract_audio(resolved, audio_format, logger)
    try:
        audio_bytes = audio_path.read_bytes()
        return Response(
            content=audio_bytes,
            media_type=_AUDIO_MIME[audio_format],
            headers={
                "Content-Length": str(len(audio_bytes)),
                "Content-Disposition": f'attachment; filename="audio.{audio_format}"',
            },
        )
    finally:
        audio_path.unlink(missing_ok=True)


@router.get("/clip/{clip_id:path}/frame")
async def get_clip_frame(
    clip_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
    time: float = Query(..., ge=0),
):
    file_path = Path(clip_id)
    resolved = _validate_tmp_path(file_path)

    if resolved.suffix.lower() not in {".mp4", ".webm", ".mkv", ".avi"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video file type.")

    frame_path = await KeyframeExtractor.extract_keyframe(resolved, time)
    if not frame_path or not frame_path.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to extract frame.")

    return Response(
        content=frame_path.read_bytes(),
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=86400"},
    )


# --- Source video operations ---

@router.get("/video/stream")
async def stream_source_video(
    request: Request,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
    path: Annotated[str, Query(description="Relative path to source video")],
):
    resolved = await _resolve_video_path(path)
    return _build_streaming_response(resolved, request)


@router.get("/video/frame")
async def get_source_frame(
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
    time: Annotated[float, Query(ge=0)],
    path: Annotated[str, Query(description="Relative path to source video")],
):
    resolved = await _resolve_video_path(path)

    frame_path = await KeyframeExtractor.extract_keyframe(resolved, time)
    if not frame_path or not frame_path.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to extract frame.")

    return Response(
        content=frame_path.read_bytes(),
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=86400"},
    )


@router.post("/reindex", response_model=ReindexResponse)
async def trigger_reindex(
    body: ReindexRequest,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
):
    target = body.target
    if target not in {"all", "all-new"} and not target.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target format.")

    task_id = await task_manager.create_task(target)

    asyncio.create_task(_run_reindex(task_id, target))

    return ReindexResponse(task_id=task_id, status="pending")


@router.get("/reindex/{task_id}/status", response_model=ReindexStatusResponse)
async def get_reindex_status(
    task_id: str,
    user: Annotated[WorkerUser, Depends(require_worker_auth)],  # pylint: disable=unused-argument
):
    task_status = await task_manager.get_status(task_id)
    if not task_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    result = None
    if task_status.status == "completed":
        result = {
            "series_name": task_status.series_name,
            "episodes_processed": task_status.episodes_processed,
            "documents_indexed": task_status.documents_indexed,
            "errors": task_status.errors,
        }

    return ReindexStatusResponse(
        task_id=task_status.task_id,
        target=task_status.target,
        status=task_status.status,
        created_at=task_status.created_at.isoformat(),
        completed_at=task_status.completed_at.isoformat() if task_status.completed_at else None,
        result=result,
        error=task_status.error,
    )


async def _run_reindex(task_id: str, target: str) -> None:
    await task_manager.start_task(task_id)
    try:
        async with ReindexService.create(logger) as service:
            async def _silent_progress(message: str, current: int, total: int) -> None:
                logger.info(f"Reindex {task_id}: {message} ({current}/{total})")

            if target == "all":
                results = await service.reindex_all(_silent_progress)
                total_eps = sum(r.episodes_processed for r in results)
                total_docs = sum(r.documents_indexed for r in results)
                all_errors: list[str] = []
                for r in results:
                    all_errors.extend(r.errors)
                await task_manager.complete_task_multi(
                    task_id, total_eps, total_docs, all_errors,
                )
            elif target == "all-new":
                results = await service.reindex_all_new(_silent_progress)
                total_eps = sum(r.episodes_processed for r in results)
                total_docs = sum(r.documents_indexed for r in results)
                all_errors = []
                for r in results:
                    all_errors.extend(r.errors)
                await task_manager.complete_task_multi(
                    task_id, total_eps, total_docs, all_errors,
                )
            else:
                result = await service.reindex_series(target, _silent_progress)
                await task_manager.complete_task(
                    task_id,
                    result.series_name,
                    result.episodes_processed,
                    result.documents_indexed,
                    result.errors,
                )
    except Exception as exc:
        logger.error(f"Reindex task {task_id} failed: {exc}", exc_info=True)
        await task_manager.fail_task(task_id, str(exc))
