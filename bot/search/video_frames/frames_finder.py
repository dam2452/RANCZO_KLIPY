import logging
from typing import (
    Any,
    List,
    Optional,
    Tuple,
)

from bot.search.infra.elastic_search_manager import (
    ElasticSearchManager,
    build_episode_restriction_filter,
    build_video_path_time_range_query,
)
from bot.settings import settings
from bot.types import VideoFrameSource
from bot.utils.constants import (
    DetectedObjectKeys,
    ElasticsearchAggregationKeys,
    ElasticsearchIndexSuffixes,
    ElasticsearchKeys,
    ElasticsearchQueryKeys,
    EpisodeMetadataKeys,
    SegmentKeys,
    VideoFrameKeys,
)
from bot.utils.log import log_system_message


def _build_index(series_name: str) -> str:
    return f"{series_name}{ElasticsearchIndexSuffixes.VIDEO_FRAMES}"


class VideoFramesFinder:
    __FRAME_SOURCE_FIELDS = [
        EpisodeMetadataKeys.EPISODE_METADATA,
        VideoFrameKeys.TIMESTAMP,
        VideoFrameKeys.FRAME_NUMBER,
        VideoFrameKeys.FRAME_TYPE,
        VideoFrameKeys.DETECTED_OBJECTS,
        VideoFrameKeys.SCENE_INFO,
        SegmentKeys.VIDEO_PATH,
        VideoFrameKeys.EPISODE_ID,
    ]

    @staticmethod
    async def find_frames_in_episode(  # pylint: disable=duplicate-code
        season: int,
        episode_number: int,
        series_name: str,
        logger: logging.Logger,
    ) -> List[VideoFrameSource]:
        await log_system_message(
            logging.INFO,
            f"Fetching frames for S{season:02d}E{episode_number:02d} in '{series_name}'.",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season}},
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: episode_number}},
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [{VideoFrameKeys.TIMESTAMP: ElasticsearchQueryKeys.ASC}],
            ElasticsearchQueryKeys.SIZE: settings.MAX_ES_RESULTS_LONG,
            ElasticsearchQueryKeys.SOURCE: VideoFramesFinder.__FRAME_SOURCE_FIELDS,
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
        frames = [h[ElasticsearchKeys.SOURCE] for h in hits]
        await log_system_message(
            logging.INFO, f"Found {len(frames)} frames for S{season:02d}E{episode_number:02d}.", logger,
        )
        return frames

    @staticmethod
    async def aggregate_scene_data(
        video_path: str,
        start_time: float,
        end_time: float,
        series_name: str,
        logger: logging.Logger,
    ) -> Tuple[int, List[dict], List[dict]]:
        await log_system_message(
            logging.INFO,
            f"Aggregating scene data by video_path in [{start_time:.2f}s, {end_time:.2f}s].",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = build_video_path_time_range_query(
            video_path=video_path,
            start_time=start_time,
            end_time=end_time,
            time_field=VideoFrameKeys.TIMESTAMP,
        )
        query[ElasticsearchQueryKeys.SIZE] = 0
        query[ElasticsearchQueryKeys.AGGS] = {
            "frame_count": {
                "value_count": {ElasticsearchQueryKeys.FIELD: VideoFrameKeys.TIMESTAMP},
            },
            "characters": {
                ElasticsearchQueryKeys.NESTED: {ElasticsearchQueryKeys.PATH: "character_appearances"},
                ElasticsearchQueryKeys.AGGS: {
                    "by_name": {
                        ElasticsearchQueryKeys.TERMS: {
                            ElasticsearchQueryKeys.FIELD: "character_appearances.name",
                            ElasticsearchQueryKeys.SIZE: 50,
                        },
                        ElasticsearchQueryKeys.AGGS: {
                            "max_confidence": {
                                "max": {ElasticsearchQueryKeys.FIELD: "character_appearances.confidence"},
                            },
                            "top_emotion": {
                                ElasticsearchQueryKeys.TERMS: {
                                    ElasticsearchQueryKeys.FIELD: "character_appearances.emotion.label",
                                    ElasticsearchQueryKeys.SIZE: 1,
                                },
                            },
                        },
                    },
                },
            },
            "objects": {
                ElasticsearchQueryKeys.NESTED: {ElasticsearchQueryKeys.PATH: "detected_objects"},
                ElasticsearchQueryKeys.AGGS: {
                    "by_class": {
                        ElasticsearchQueryKeys.TERMS: {
                            ElasticsearchQueryKeys.FIELD: "detected_objects.class",
                            ElasticsearchQueryKeys.SIZE: 50,
                        },
                        ElasticsearchQueryKeys.AGGS: {
                            "total_count": {
                                "sum": {ElasticsearchQueryKeys.FIELD: "detected_objects.count"},
                            },
                        },
                    },
                },
            },
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        aggs = response.get(ElasticsearchKeys.AGGREGATIONS, {})

        frame_count = aggs.get("frame_count", {}).get(ElasticsearchQueryKeys.VALUE, 0) or 0

        character_buckets = aggs.get("characters", {}).get("by_name", {}).get(ElasticsearchKeys.BUCKETS, [])
        characters = [
            {
                "name": b[ElasticsearchKeys.KEY],
                "confidence": b.get("max_confidence", {}).get(ElasticsearchQueryKeys.VALUE) or 0.0,
                "emotion_label": (b.get("top_emotion", {}).get(ElasticsearchKeys.BUCKETS) or [{}])[0].get(ElasticsearchKeys.KEY),
                "frame_count": b[ElasticsearchKeys.DOC_COUNT],
            }
            for b in character_buckets
        ]

        object_buckets = aggs.get("objects", {}).get("by_class", {}).get(ElasticsearchKeys.BUCKETS, [])
        objects = [
            {
                "name": b[ElasticsearchKeys.KEY],
                "total_count": int(b.get("total_count", {}).get(ElasticsearchQueryKeys.VALUE) or 0),
                "frame_count": b[ElasticsearchKeys.DOC_COUNT],
            }
            for b in object_buckets
        ]

        await log_system_message(
            logging.INFO,
            f"Scene agg: {frame_count} frames, {len(characters)} chars, {len(objects)} objects.",
            logger,
        )
        return frame_count, characters, objects

    @staticmethod
    async def find_frames_in_time_range(
        season: int,
        episode_number: int,
        start_time: float,
        end_time: float,
        series_name: str,
        logger: logging.Logger,
    ) -> List[VideoFrameSource]:
        await log_system_message(
            logging.INFO,
            f"Fetching frames in [{start_time:.2f}s, {end_time:.2f}s] in S{season:02d}E{episode_number:02d}.",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season}},
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: episode_number}},
                        {
                            ElasticsearchQueryKeys.RANGE: {
                                VideoFrameKeys.TIMESTAMP: {
                                    ElasticsearchQueryKeys.GTE: start_time,
                                    ElasticsearchQueryKeys.LTE: end_time,
                                },
                            },
                        },
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [{VideoFrameKeys.TIMESTAMP: ElasticsearchQueryKeys.ASC}],
            ElasticsearchQueryKeys.SIZE: 50,
            ElasticsearchQueryKeys.SOURCE: VideoFramesFinder.__FRAME_SOURCE_FIELDS,
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
        frames = [h[ElasticsearchKeys.SOURCE] for h in hits]
        await log_system_message(
            logging.INFO,
            f"Found {len(frames)} frames in time range for S{season:02d}E{episode_number:02d}.",
            logger,
        )
        return frames

    @staticmethod
    async def find_frames_near_timestamp(
        season: int,
        episode_number: int,
        timestamp: float,
        radius_seconds: float,
        series_name: str,
        logger: logging.Logger,
    ) -> List[VideoFrameSource]:
        await log_system_message(
            logging.INFO,
            f"Fetching frames near {timestamp:.2f}s (±{radius_seconds}s) in S{season:02d}E{episode_number:02d}.",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season}},
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: episode_number}},
                        {
                            ElasticsearchQueryKeys.RANGE: {
                                VideoFrameKeys.TIMESTAMP: {
                                    ElasticsearchQueryKeys.GT: timestamp - radius_seconds,
                                    ElasticsearchQueryKeys.LT: timestamp + radius_seconds,
                                },
                            },
                        },
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [{VideoFrameKeys.TIMESTAMP: ElasticsearchQueryKeys.ASC}],
            ElasticsearchQueryKeys.SIZE: 100,
            ElasticsearchQueryKeys.SOURCE: VideoFramesFinder.__FRAME_SOURCE_FIELDS,
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
        return [h[ElasticsearchKeys.SOURCE] for h in hits]

    @staticmethod
    async def find_frames_with_detected_object(
        object_class: str,
        series_name: str,
        logger: logging.Logger,
        seasons: Optional[List[int]] = None,
        episodes: Optional[List[Tuple[int, int]]] = None,
    ) -> List[VideoFrameSource]:
        await log_system_message(
            logging.INFO, f"Fetching frames with object '{object_class}' in '{series_name}'.", logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        must_clauses: List[dict[str, Any]] = [
            {
                ElasticsearchQueryKeys.NESTED: {
                    ElasticsearchQueryKeys.PATH: VideoFrameKeys.DETECTED_OBJECTS,
                    ElasticsearchQueryKeys.QUERY: {
                        ElasticsearchQueryKeys.TERM: {DetectedObjectKeys.OBJECT_CLASS_FIELD: object_class},
                    },
                },
            },
        ]
        if seasons:
            must_clauses.append({ElasticsearchQueryKeys.TERMS: {EpisodeMetadataKeys.SEASON_FIELD: seasons}})
        episode_filter = build_episode_restriction_filter(episodes) if episodes else None
        if episode_filter:
            must_clauses.append(episode_filter)

        object_count_field = f"{VideoFrameKeys.DETECTED_OBJECTS}.count"
        query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {ElasticsearchQueryKeys.FILTER: must_clauses},
            },
            ElasticsearchQueryKeys.SORT: [
                {
                    object_count_field: {
                        ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.DESC,
                        ElasticsearchQueryKeys.NESTED: {
                            ElasticsearchQueryKeys.PATH: VideoFrameKeys.DETECTED_OBJECTS,
                            ElasticsearchQueryKeys.FILTER: {
                                ElasticsearchQueryKeys.TERM: {DetectedObjectKeys.OBJECT_CLASS_FIELD: object_class},
                            },
                        },
                        ElasticsearchQueryKeys.MODE: ElasticsearchQueryKeys.MAX,
                    },
                },
            ],
            ElasticsearchQueryKeys.SIZE: settings.MAX_ES_RESULTS_LONG,
            ElasticsearchQueryKeys.SOURCE: VideoFramesFinder.__FRAME_SOURCE_FIELDS,
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
        frames = [h[ElasticsearchKeys.SOURCE] for h in hits]
        await log_system_message(
            logging.INFO, f"Found {len(frames)} frames with object '{object_class}'.", logger,
        )
        return frames

    @staticmethod
    async def get_all_detected_objects(  # pylint: disable=duplicate-code
        series_name: str,
        logger: logging.Logger,
    ) -> List[str]:
        await log_system_message(
            logging.INFO, f"Fetching all detected object classes for series '{series_name}'.", logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = {
            ElasticsearchQueryKeys.SIZE: 0,
            ElasticsearchQueryKeys.AGGS: {
                ElasticsearchAggregationKeys.OBJECTS: {
                    ElasticsearchQueryKeys.NESTED: {ElasticsearchQueryKeys.PATH: VideoFrameKeys.DETECTED_OBJECTS},
                    ElasticsearchQueryKeys.AGGS: {
                        ElasticsearchAggregationKeys.CLASSES: {
                            ElasticsearchQueryKeys.TERMS: {
                                ElasticsearchQueryKeys.FIELD: DetectedObjectKeys.OBJECT_CLASS_FIELD,
                                ElasticsearchQueryKeys.SIZE: 500,
                                ElasticsearchQueryKeys.ORDER: {ElasticsearchQueryKeys.KEY: ElasticsearchQueryKeys.ASC},
                            },
                        },
                    },
                },
            },
        }

        response = await es.search(index=_build_index(series_name), body=query, ignore_unavailable=True)
        buckets = (
            response[ElasticsearchKeys.AGGREGATIONS]
            [ElasticsearchAggregationKeys.OBJECTS]
            [ElasticsearchAggregationKeys.CLASSES]
            [ElasticsearchKeys.BUCKETS]
        )
        classes = [b[ElasticsearchKeys.KEY] for b in buckets]
        await log_system_message(logging.INFO, f"Found {len(classes)} detected object classes.", logger)
        return classes
