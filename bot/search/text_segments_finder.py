import logging
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

from bot.search.filter_applicator import FilterApplicator
from bot.search.infra.elastic_search_manager import (
    ElasticSearchManager,
    build_episode_restriction_filter,
    build_fuzzy_with_boost_query,
)
from bot.settings import settings
from bot.types import (
    BaseSegment,
    ElasticsearchSegment,
    EpisodeInfo,
    SearchFilter,
    SeasonInfoDict,
    SegmentWithScore,
    TranscriptionContext,
)
from bot.utils.constants import (
    ElasticsearchAggregationKeys,
    ElasticsearchIndexSuffixes,
    ElasticsearchKeys,
    ElasticsearchQueryKeys,
    EpisodeMetadataKeys,
    SegmentKeys,
    TranscriptionContextKeys,
)
from bot.utils.log import log_system_message


class TextSegmentsFinder:
    __TEXT_SEGMENT_SOURCE_FIELDS = [
        SegmentKeys.TEXT,
        SegmentKeys.START_TIME,
        SegmentKeys.END_TIME,
        SegmentKeys.START,
        SegmentKeys.END,
        SegmentKeys.SEGMENT_ID,
        SegmentKeys.ID,
        SegmentKeys.VIDEO_PATH,
        EpisodeMetadataKeys.EPISODE_METADATA,
        EpisodeMetadataKeys.EPISODE_INFO,
    ]

    @staticmethod
    def __hit_score(hit: Dict[str, Any]) -> float:
        raw = hit.get(ElasticsearchKeys.SCORE)
        if raw is None:
            return 0.0
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def __segment_score(segment: SegmentWithScore) -> float:
        raw = segment.get(ElasticsearchKeys.SCORE)
        if raw is None:
            return 0.0
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def is_segment_overlap(
            previous_segment: ElasticsearchSegment,
            segment: ElasticsearchSegment,
            start_time: float,
    ) -> bool:
        if not previous_segment:
            return False

        prev_metadata = previous_segment.get(EpisodeMetadataKeys.EPISODE_METADATA, {})
        curr_metadata = segment[EpisodeMetadataKeys.EPISODE_METADATA]

        prev_season = prev_metadata.get(EpisodeMetadataKeys.SEASON)
        curr_season = curr_metadata[EpisodeMetadataKeys.SEASON]

        prev_episode = prev_metadata.get(EpisodeMetadataKeys.EPISODE_NUMBER)
        curr_episode = curr_metadata[EpisodeMetadataKeys.EPISODE_NUMBER]

        prev_end_time = previous_segment.get(
            SegmentKeys.END_TIME,
            previous_segment.get(SegmentKeys.END, 0),
        )

        return (
            prev_season == curr_season and
            prev_episode == curr_episode and
            start_time <= prev_end_time
        )

    @staticmethod
    def __apply_search_filter_to_query(query: Dict[str, Any], search_filter: SearchFilter) -> None:
        extra = FilterApplicator.build_es_season_episode_clauses(search_filter)
        filter_list = query[ElasticsearchQueryKeys.QUERY][ElasticsearchQueryKeys.BOOL][ElasticsearchQueryKeys.FILTER]
        filter_list.extend(extra)

        title = search_filter.get("episode_title")
        if title:
            filter_list.append({
                ElasticsearchQueryKeys.MATCH: {
                    EpisodeMetadataKeys.TITLE_FIELD: {
                        ElasticsearchQueryKeys.QUERY: title,
                        ElasticsearchQueryKeys.FUZZINESS: ElasticsearchQueryKeys.AUTO,
                    },
                },
            })

    @staticmethod
    def __merge_overlapping_segment(
        incoming: SegmentWithScore,
        collected: List[SegmentWithScore],
        incoming_start: float,
        incoming_end: float,
    ) -> bool:
        for i, existing_segment in enumerate(collected):
            existing_start = existing_segment[SegmentKeys.START_TIME] - settings.EXTEND_BEFORE
            existing_end = existing_segment[SegmentKeys.END_TIME] + settings.EXTEND_AFTER

            seg_metadata = incoming.get(EpisodeMetadataKeys.EPISODE_METADATA, {})
            existing_metadata = existing_segment.get(EpisodeMetadataKeys.EPISODE_METADATA, {})

            seg_season = seg_metadata.get(EpisodeMetadataKeys.SEASON)
            existing_season = existing_metadata.get(EpisodeMetadataKeys.SEASON)

            seg_episode = seg_metadata.get(EpisodeMetadataKeys.EPISODE_NUMBER)
            existing_episode = existing_metadata.get(EpisodeMetadataKeys.EPISODE_NUMBER)

            if (
                seg_season == existing_season and
                seg_episode == existing_episode and
                incoming_start <= existing_end and
                incoming_end >= existing_start
            ):
                collected[i][SegmentKeys.START_TIME] = min(
                    existing_segment[SegmentKeys.START_TIME],
                    incoming[SegmentKeys.START_TIME],
                )
                collected[i][SegmentKeys.END_TIME] = max(
                    existing_segment[SegmentKeys.END_TIME],
                    incoming[SegmentKeys.END_TIME],
                )
                collected[i][ElasticsearchKeys.SCORE] = max(
                    TextSegmentsFinder.__segment_score(existing_segment),
                    TextSegmentsFinder.__segment_score(incoming),
                )
                return True
        return False

    @staticmethod
    def __deduplicate_hits(hits: List[Dict[str, Any]]) -> List[SegmentWithScore]:
        unique_segments: List[SegmentWithScore] = []
        seen_segments = set()
        for hit in hits:
            segment: SegmentWithScore = hit[ElasticsearchKeys.SOURCE]
            segment[ElasticsearchKeys.SCORE] = TextSegmentsFinder.__hit_score(hit)
            segment_key = (
                segment.get(EpisodeMetadataKeys.EPISODE_METADATA, {}).get(EpisodeMetadataKeys.SEASON),
                segment.get(EpisodeMetadataKeys.EPISODE_METADATA, {}).get(EpisodeMetadataKeys.EPISODE_NUMBER),
                segment.get(SegmentKeys.START_TIME),
                segment.get(SegmentKeys.END_TIME),
            )
            if segment_key not in seen_segments:
                seen_segments.add(segment_key)
                start_time = segment[SegmentKeys.START_TIME] - settings.EXTEND_BEFORE
                end_time = segment[SegmentKeys.END_TIME] + settings.EXTEND_AFTER
                if not TextSegmentsFinder.__merge_overlapping_segment(segment, unique_segments, start_time, end_time):
                    unique_segments.append(segment)
        return unique_segments

    @staticmethod
    async def find_segment_by_quote(
            quote: str, logger: logging.Logger, series_name: str, season_filter: Optional[int] = None,
            episode_filter: Optional[int] = None,
            size: int = 1,
            search_filter: Optional[SearchFilter] = None,
    ) -> Optional[Union[SegmentWithScore, List[SegmentWithScore]]]:
        await log_system_message(
            logging.INFO,
            f"Searching for quote: '{quote}' in series '{series_name}' with filters - Season: {season_filter}, Episode: {episode_filter}",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        query = build_fuzzy_with_boost_query(
            field=SegmentKeys.TEXT,
            query=quote,
            filter_clauses=[
                {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SERIES_NAME_FIELD: series_name}},
            ],
        )
        query[ElasticsearchQueryKeys.SORT] = [
            {ElasticsearchKeys.SCORE: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.DESC}},
            {EpisodeMetadataKeys.SEASON_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
            {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
            {SegmentKeys.START_TIME: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
        ]
        query[ElasticsearchQueryKeys.SOURCE] = TextSegmentsFinder.__TEXT_SEGMENT_SOURCE_FIELDS

        if season_filter:
            query[ElasticsearchQueryKeys.QUERY][ElasticsearchQueryKeys.BOOL][ElasticsearchQueryKeys.FILTER].append(
                {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season_filter}},
            )

        if episode_filter:
            query[ElasticsearchQueryKeys.QUERY][ElasticsearchQueryKeys.BOOL][ElasticsearchQueryKeys.FILTER].append(
                {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: episode_filter}},
            )

        if search_filter:
            TextSegmentsFinder.__apply_search_filter_to_query(query, search_filter)

        hits = (await es.search(index=index, body=query, size=size, ignore_unavailable=True))[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]

        if not hits:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        unique_segments = TextSegmentsFinder.__deduplicate_hits(hits)

        await log_system_message(
            logging.INFO, f"Found {len(unique_segments)} unique segments after merging.",
            logger,
        )

        if unique_segments:
            return unique_segments[0] if size == 1 else unique_segments

        return None

    @staticmethod
    def __build_episode_restriction_clause(
        episode_keys: Iterable[Tuple[int, int]],
    ) -> Optional[Dict[str, Any]]:
        return build_episode_restriction_filter(episode_keys)

    _MAX_CLAUSES_PER_QUERY: int = 80
    _SCENE_GAP_SECONDS: float = 30.0
    _BATCH_FETCH_SIZE: int = 10000

    @staticmethod
    def _merge_timestamps_into_scenes(
        timestamps: List[float],
    ) -> List[Tuple[float, float]]:
        sorted_ts = sorted(set(timestamps))
        if not sorted_ts:
            return []
        scenes: List[Tuple[float, float]] = []
        scene_start = sorted_ts[0]
        scene_end = sorted_ts[0]
        for ts in sorted_ts[1:]:
            if ts - scene_end <= TextSegmentsFinder._SCENE_GAP_SECONDS:
                scene_end = ts
            else:
                scenes.append((scene_start, scene_end))
                scene_start = ts
                scene_end = ts
        scenes.append((scene_start, scene_end))
        return scenes

    @staticmethod
    def _build_timestamp_clauses(
        episode_ts_map: Dict[Tuple[Optional[int], Optional[int]], List[float]],
    ) -> List[Dict[str, Any]]:
        clauses: List[Dict[str, Any]] = []
        for (season, episode), timestamps in episode_ts_map.items():
            if season is None or episode is None:
                continue
            for scene_start, scene_end in TextSegmentsFinder._merge_timestamps_into_scenes(timestamps):
                clauses.append({
                    ElasticsearchQueryKeys.BOOL: {
                        ElasticsearchQueryKeys.FILTER: [
                            {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season}},
                            {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: episode}},
                            {ElasticsearchQueryKeys.RANGE: {SegmentKeys.START_TIME: {ElasticsearchQueryKeys.LTE: scene_end}}},
                            {ElasticsearchQueryKeys.RANGE: {SegmentKeys.END_TIME: {ElasticsearchQueryKeys.GTE: scene_start}}},
                        ],
                    },
                })
        return clauses

    @staticmethod
    def _build_interval_batch_query(
        series_name: str,
        interval_clauses: List[Dict[str, Any]],
        search_filter: SearchFilter,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SERIES_NAME_FIELD: series_name}},
                    ],
                    ElasticsearchQueryKeys.SHOULD: interval_clauses,
                    ElasticsearchQueryKeys.MINIMUM_SHOULD_MATCH: 1,
                },
            },
            ElasticsearchQueryKeys.SORT: [
                {EpisodeMetadataKeys.SEASON_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
                {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
                {SegmentKeys.START_TIME: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
            ],
            ElasticsearchQueryKeys.SOURCE: TextSegmentsFinder.__TEXT_SEGMENT_SOURCE_FIELDS,
        }
        TextSegmentsFinder.__apply_search_filter_to_query(query, search_filter)
        return query

    @staticmethod
    async def _search_batched_clauses(
        es: Any,
        index: str,
        series_name: str,
        all_clauses: List[Dict[str, Any]],
        search_filter: SearchFilter,
    ) -> List[Dict[str, Any]]:
        all_hits: List[Dict[str, Any]] = []
        seen_ids: set = set()
        for i in range(0, len(all_clauses), TextSegmentsFinder._MAX_CLAUSES_PER_QUERY):
            batch = all_clauses[i:i + TextSegmentsFinder._MAX_CLAUSES_PER_QUERY]
            query = TextSegmentsFinder._build_interval_batch_query(series_name, batch, search_filter)
            response = await es.search(
                index=index, body=query,
                size=TextSegmentsFinder._BATCH_FETCH_SIZE, ignore_unavailable=True,
            )
            batch_hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
            for hit in batch_hits:
                hit_id = hit.get(ElasticsearchKeys.ID)
                if hit_id not in seen_ids:
                    seen_ids.add(hit_id)
                    all_hits.append(hit)
        return all_hits

    @staticmethod
    async def find_segments_by_frame_timestamps(
            logger: logging.Logger,
            series_name: str,
            frame_keys: Iterable[Tuple[Optional[int], Optional[int], float]],
            search_filter: SearchFilter,
    ) -> List[SegmentWithScore]:
        await log_system_message(
            logging.INFO,
            f"Fetching text segments for series '{series_name}' by frame timestamps (ES-side filtering).",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        episode_ts_map: Dict[Tuple[Optional[int], Optional[int]], List[float]] = {}
        for season, episode, ts in frame_keys:
            episode_ts_map.setdefault((season, episode), []).append(ts)

        if not episode_ts_map:
            return []

        all_clauses = TextSegmentsFinder._build_timestamp_clauses(episode_ts_map)

        if not all_clauses:
            return []

        await log_system_message(
            logging.INFO,
            f"Built {len(all_clauses)} timestamp clauses for {len(episode_ts_map)} episodes.",
            logger,
        )

        all_hits = await TextSegmentsFinder._search_batched_clauses(
            es, index, series_name, all_clauses, search_filter,
        )

        if not all_hits:
            await log_system_message(logging.INFO, "No segments found matching frame timestamps.", logger)
            return []

        for hit in all_hits:
            hit[ElasticsearchKeys.SCORE] = TextSegmentsFinder.__hit_score(hit)

        unique_segments = TextSegmentsFinder.__deduplicate_hits(all_hits)
        await log_system_message(
            logging.INFO,
            f"Found {len(unique_segments)} unique segments by frame timestamps.",
            logger,
        )
        return unique_segments

    @staticmethod
    async def find_segments_by_filter_only(
            logger: logging.Logger,
            series_name: str,
            search_filter: SearchFilter,
            size: int = 1000,
            restrict_episode_keys: Optional[Iterable[Tuple[int, int]]] = None,
    ) -> List[SegmentWithScore]:
        await log_system_message(
            logging.INFO,
            f"Fetching text segments for series '{series_name}' constrained only by filter (no quote).",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        query: Dict[str, Any] = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SERIES_NAME_FIELD: series_name}},
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [
                {EpisodeMetadataKeys.SEASON_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
                {EpisodeMetadataKeys.EPISODE_NUMBER_FIELD: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
                {SegmentKeys.START_TIME: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
            ],
            ElasticsearchQueryKeys.SOURCE: TextSegmentsFinder.__TEXT_SEGMENT_SOURCE_FIELDS,
        }

        TextSegmentsFinder.__apply_search_filter_to_query(query, search_filter)

        restriction = TextSegmentsFinder.__build_episode_restriction_clause(restrict_episode_keys)
        if restriction is None:
            await log_system_message(
                logging.INFO,
                "Filter-only search: no eligible episodes after video-frame prefilter.",
                logger,
            )
            return []
        query[ElasticsearchQueryKeys.QUERY][ElasticsearchQueryKeys.BOOL][
            ElasticsearchQueryKeys.FILTER
        ].append(restriction)

        hits = (await es.search(index=index, body=query, size=size, ignore_unavailable=True))[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]

        if not hits:
            await log_system_message(logging.INFO, "No segments found matching filter-only query.", logger)
            return []

        for hit in hits:
            hit[ElasticsearchKeys.SCORE] = TextSegmentsFinder.__hit_score(hit)

        unique_segments = TextSegmentsFinder.__deduplicate_hits(hits)
        await log_system_message(
            logging.INFO,
            f"Found {len(unique_segments)} unique segments after filter-only search.",
            logger,
        )
        return unique_segments

    @staticmethod
    async def find_segment_with_context(
            quote: str, logger: logging.Logger, series_name: str, context_size: int = 30,
            season_filter: Optional[int] = None, episode_filter: Optional[int] = None,
            index: Optional[str] = None,
            search_filter: Optional[SearchFilter] = None,
    ) -> Optional[TranscriptionContext]:
        await log_system_message(
            logging.INFO,
            f"Searching for quote: '{quote}' in series '{series_name}' with context size: {context_size}. Season: {season_filter}, Episode: {episode_filter}",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        if index is None:
            index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        segment = await TextSegmentsFinder.find_segment_by_quote(
            quote, logger, series_name, season_filter, episode_filter, search_filter=search_filter,
        )
        if not segment:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        segment = segment[0] if isinstance(segment, list) else segment
        episode_data = segment.get(
            EpisodeMetadataKeys.EPISODE_METADATA,
            segment.get(EpisodeMetadataKeys.EPISODE_INFO, {}),
        )
        segment_id = segment.get(SegmentKeys.SEGMENT_ID, segment.get(SegmentKeys.ID))
        if segment_id is None:
            await log_system_message(logging.INFO, "Target segment has no segment ID; cannot fetch context.", logger)
            return None

        context_segments = await TextSegmentsFinder._fetch_context_segments(
            es, index, episode_data, segment_id, context_size,
        )

        segment_start = segment.get(SegmentKeys.START_TIME, segment.get(SegmentKeys.START))
        segment_end = segment.get(SegmentKeys.END_TIME, segment.get(SegmentKeys.END))
        unique_context_segments = TextSegmentsFinder.__build_unique_segments(
            context_segments, segment_id, segment, segment_start, segment_end,
        )

        await log_system_message(logging.INFO, f"Found {len(unique_context_segments)} unique segments for context.", logger)

        overall_start_time = min(seg[SegmentKeys.START] for seg in unique_context_segments)
        overall_end_time = max(seg[SegmentKeys.END] for seg in unique_context_segments)

        result = {
            TranscriptionContextKeys.TARGET: segment,
            TranscriptionContextKeys.CONTEXT: unique_context_segments,
            TranscriptionContextKeys.OVERALL_START_TIME: overall_start_time,
            TranscriptionContextKeys.OVERALL_END_TIME: overall_end_time,
        }
        return result

    @staticmethod
    async def _fetch_context_segments(
            es: Any,
            index: str,
            episode_data: ElasticsearchSegment,
            segment_id: int,
            context_size: int,
    ) -> List[BaseSegment]:
        season_field = EpisodeMetadataKeys.SEASON_FIELD
        episode_field = EpisodeMetadataKeys.EPISODE_NUMBER_FIELD

        context_query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {season_field: episode_data[EpisodeMetadataKeys.SEASON]}},
                        {
                            ElasticsearchQueryKeys.TERM: {
                                episode_field: episode_data[EpisodeMetadataKeys.EPISODE_NUMBER],
                            },
                        },
                        {
                            ElasticsearchQueryKeys.RANGE: {
                                SegmentKeys.SEGMENT_ID: {
                                    ElasticsearchQueryKeys.GTE: segment_id - context_size,
                                    ElasticsearchQueryKeys.LTE: segment_id + context_size,
                                },
                            },
                        },
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [{SegmentKeys.SEGMENT_ID: ElasticsearchQueryKeys.ASC}],
            ElasticsearchQueryKeys.SIZE: context_size * 2 + 1,
            ElasticsearchQueryKeys.SOURCE: [
                SegmentKeys.SEGMENT_ID,
                SegmentKeys.ID,
                SegmentKeys.TEXT,
                SegmentKeys.START_TIME,
                SegmentKeys.END_TIME,
                SegmentKeys.START,
                SegmentKeys.END,
            ],
        }

        context_response = await es.search(index=index, body=context_query, ignore_unavailable=True)
        return [{
            SegmentKeys.ID: hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.SEGMENT_ID, hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.ID)),
            SegmentKeys.TEXT: hit[ElasticsearchKeys.SOURCE][SegmentKeys.TEXT],
            SegmentKeys.START: hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.START_TIME, hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.START)),
            SegmentKeys.END: hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.END_TIME, hit[ElasticsearchKeys.SOURCE].get(SegmentKeys.END)),
        } for hit in context_response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]]

    @staticmethod
    def __build_unique_segments(
            context_segments: List[BaseSegment],
            segment_id: int,
            segment: ElasticsearchSegment,
            segment_start: float,
            segment_end: float,
    ) -> List[BaseSegment]:
        unique_context_segments = []
        seen_keys = set()

        target_segment = {
            SegmentKeys.ID: segment_id,
            SegmentKeys.TEXT: segment[SegmentKeys.TEXT],
            SegmentKeys.START: segment_start,
            SegmentKeys.END: segment_end,
        }

        all_segments = context_segments + [target_segment]

        for seg in all_segments:
            seg_key = (
                seg.get(SegmentKeys.ID),
                seg.get(SegmentKeys.START),
                seg.get(SegmentKeys.END),
            )
            if seg_key not in seen_keys:
                seen_keys.add(seg_key)
                unique_context_segments.append(seg)
        return unique_context_segments

    @staticmethod
    async def find_video_path_by_episode(  # pylint: disable=duplicate-code
            season: int, episode_number: int, logger: logging.Logger,
            index: str = settings.ES_TRANSCRIPTION_INDEX,
    ) -> Optional[str]:
        await log_system_message(
            logging.INFO,
            f"Searching for video path with filters - Season: {season}, Episode: {episode_number}",
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
            ElasticsearchQueryKeys.SOURCE: [SegmentKeys.VIDEO_PATH],
        }

        response = await es.search(index=index, body=query, size=1, ignore_unavailable=True)
        hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]

        if not hits:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        segment = hits[0][ElasticsearchKeys.SOURCE]
        video_path = segment.get(SegmentKeys.VIDEO_PATH, None)

        if video_path:
            await log_system_message(logging.INFO, f"Found video path: {video_path}", logger)
            return video_path

        await log_system_message(logging.INFO, "Video path not found in the segment.", logger)
        return None

    @staticmethod
    async def find_episodes_by_season(season: int, logger: logging.Logger, index: str = settings.ES_TRANSCRIPTION_INDEX) -> Optional[List[EpisodeInfo]]:
        await log_system_message(logging.INFO, f"Searching for episodes in season {season}", logger)
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)

        query = {
            ElasticsearchQueryKeys.SIZE: 0,
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.TERM: {EpisodeMetadataKeys.SEASON_FIELD: season},
            },
            ElasticsearchQueryKeys.AGGS: {
                ElasticsearchAggregationKeys.UNIQUE_EPISODES: {
                    ElasticsearchQueryKeys.TERMS: {
                        ElasticsearchQueryKeys.FIELD: EpisodeMetadataKeys.EPISODE_NUMBER_FIELD,
                        ElasticsearchQueryKeys.SIZE: 1000,
                        ElasticsearchQueryKeys.ORDER: {
                            ElasticsearchQueryKeys.KEY: ElasticsearchQueryKeys.ASC,
                        },
                    },
                    ElasticsearchQueryKeys.AGGS: {
                        EpisodeMetadataKeys.EPISODE_METADATA: {
                            ElasticsearchQueryKeys.TOP_HITS: {
                                ElasticsearchQueryKeys.SIZE: 1,
                                ElasticsearchQueryKeys.SOURCE: {
                                    ElasticsearchQueryKeys.INCLUDES: [
                                        EpisodeMetadataKeys.TITLE_FIELD,
                                        EpisodeMetadataKeys.PREMIERE_DATE_FIELD,
                                        EpisodeMetadataKeys.VIEWERSHIP_FIELD,
                                        EpisodeMetadataKeys.EPISODE_NUMBER_FIELD,
                                        SegmentKeys.VIDEO_PATH,
                                    ],
                                },
                            },
                        },
                        ElasticsearchAggregationKeys.MAX_END_TIME: {
                            ElasticsearchQueryKeys.MAX: {
                                ElasticsearchQueryKeys.FIELD: SegmentKeys.END_TIME,
                            },
                        },
                    },
                },
            },
        }

        response = await es.search(index=index, body=query, ignore_unavailable=True)
        buckets = response[ElasticsearchKeys.AGGREGATIONS][ElasticsearchAggregationKeys.UNIQUE_EPISODES][ElasticsearchKeys.BUCKETS]

        if not buckets:
            await log_system_message(logging.INFO, f"No episodes found for season {season}.", logger)
            return None

        episodes = []
        for bucket in buckets:
            hits_data = bucket[EpisodeMetadataKeys.EPISODE_METADATA][ElasticsearchKeys.HITS]
            source_data = hits_data[ElasticsearchKeys.HITS][0][ElasticsearchKeys.SOURCE]
            episode_metadata = source_data[EpisodeMetadataKeys.EPISODE_METADATA]

            episode = {
                EpisodeMetadataKeys.EPISODE_NUMBER: episode_metadata.get(
                    EpisodeMetadataKeys.EPISODE_NUMBER,
                ),
                EpisodeMetadataKeys.TITLE: episode_metadata.get(EpisodeMetadataKeys.TITLE, "Unknown"),
                EpisodeMetadataKeys.PREMIERE_DATE: episode_metadata.get(EpisodeMetadataKeys.PREMIERE_DATE, "Unknown"),
                EpisodeMetadataKeys.VIEWERSHIP: episode_metadata.get(EpisodeMetadataKeys.VIEWERSHIP, "Unknown"),
                SegmentKeys.VIDEO_PATH: source_data.get(SegmentKeys.VIDEO_PATH),
                "duration": bucket.get(ElasticsearchAggregationKeys.MAX_END_TIME, {}).get(ElasticsearchAggregationKeys.VALUE),
            }
            episodes.append(episode)

        await log_system_message(logging.INFO, f"Found {len(episodes)} episodes for season {season}.", logger)
        return episodes

    @staticmethod
    async def get_season_details_from_elastic(
            logger: logging.Logger,
            series_name: str,
    ) -> SeasonInfoDict:
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        agg_query = {
            ElasticsearchQueryKeys.SIZE: 0,
            ElasticsearchQueryKeys.AGGS: {
                ElasticsearchAggregationKeys.SEASONS: {
                    ElasticsearchQueryKeys.TERMS: {
                        ElasticsearchQueryKeys.FIELD: EpisodeMetadataKeys.SEASON_FIELD,
                        ElasticsearchQueryKeys.SIZE: 1000,
                        ElasticsearchQueryKeys.ORDER: {ElasticsearchQueryKeys.KEY: ElasticsearchQueryKeys.ASC},
                    },
                    ElasticsearchQueryKeys.AGGS: {
                        ElasticsearchAggregationKeys.UNIQUE_EPISODES: {
                            ElasticsearchQueryKeys.CARDINALITY: {
                                ElasticsearchQueryKeys.FIELD: EpisodeMetadataKeys.EPISODE_NUMBER_FIELD,
                            },
                        },
                    },
                },
            },
        }

        await log_system_message(logging.INFO, "Fetching season details via Elasticsearch aggregation.", logger)
        response = await es.search(index=index, body=agg_query, ignore_unavailable=True)
        buckets = response[ElasticsearchKeys.AGGREGATIONS][ElasticsearchAggregationKeys.SEASONS][ElasticsearchKeys.BUCKETS]

        season_dict = {}
        for bucket in buckets:
            season_key = str(bucket[ElasticsearchKeys.KEY])
            episodes_count = bucket[ElasticsearchAggregationKeys.UNIQUE_EPISODES][ElasticsearchAggregationKeys.VALUE]
            season_dict[season_key] = episodes_count

        await log_system_message(logging.INFO, f"Season details: {season_dict}", logger)
        return season_dict

    @staticmethod
    async def find_segments_in_time_range(
            video_path: str,
            start_time: float,
            end_time: float,
            logger: logging.Logger,
            series_name: str,
    ) -> List[BaseSegment]:
        await log_system_message(
            logging.INFO,
            f"Fetching segments for video_path='{video_path}' time=[{start_time}, {end_time}]",
            logger,
        )
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        query = {
            ElasticsearchQueryKeys.QUERY: {
                ElasticsearchQueryKeys.BOOL: {
                    ElasticsearchQueryKeys.FILTER: [
                        {ElasticsearchQueryKeys.TERM: {SegmentKeys.VIDEO_PATH: video_path}},
                        {
                            ElasticsearchQueryKeys.RANGE: {
                                SegmentKeys.START_TIME: {
                                    ElasticsearchQueryKeys.GTE: start_time,
                                    ElasticsearchQueryKeys.LTE: end_time,
                                },
                            },
                        },
                    ],
                },
            },
            ElasticsearchQueryKeys.SORT: [
                {SegmentKeys.START_TIME: {ElasticsearchQueryKeys.ORDER: ElasticsearchQueryKeys.ASC}},
            ],
            ElasticsearchQueryKeys.SOURCE: [
                SegmentKeys.START_TIME,
                SegmentKeys.END_TIME,
                SegmentKeys.TEXT,
                "speaker",
            ],
        }

        _PAGE_SIZE = 1000
        all_hits = []
        search_after = None

        while True:
            if search_after:
                query[ElasticsearchQueryKeys.SEARCH_AFTER] = search_after
            response = await es.search(index=index, body=query, size=_PAGE_SIZE, ignore_unavailable=True)
            page_hits = response[ElasticsearchKeys.HITS][ElasticsearchKeys.HITS]
            all_hits.extend(page_hits)
            if len(page_hits) < _PAGE_SIZE:
                break
            search_after = page_hits[-1]["sort"]

        await log_system_message(logging.INFO, f"Found {len(all_hits)} segments in time range.", logger)
        return [hit[ElasticsearchKeys.SOURCE] for hit in all_hits]

    @staticmethod
    async def get_index_stats(logger: logging.Logger, series_name: str) -> Dict[str, Any]:
        es = await ElasticSearchManager.connect_to_elasticsearch(logger)
        index = f"{series_name}{ElasticsearchIndexSuffixes.TEXT_SEGMENTS}"

        agg_query = {
            ElasticsearchQueryKeys.SIZE: 0,
            ElasticsearchQueryKeys.AGGS: {
                "seasons": {
                    ElasticsearchQueryKeys.TERMS: {
                        ElasticsearchQueryKeys.FIELD: EpisodeMetadataKeys.SEASON_FIELD,
                        ElasticsearchQueryKeys.SIZE: 1000,
                    },
                    ElasticsearchQueryKeys.AGGS: {
                        "episodes": {
                            ElasticsearchQueryKeys.TERMS: {
                                ElasticsearchQueryKeys.FIELD: EpisodeMetadataKeys.EPISODE_NUMBER_FIELD,
                                ElasticsearchQueryKeys.SIZE: 1000,
                            },
                            ElasticsearchQueryKeys.AGGS: {
                                "max_end": {
                                    ElasticsearchQueryKeys.MAX: {
                                        ElasticsearchQueryKeys.FIELD: SegmentKeys.END_TIME,
                                    },
                                },
                                "min_start": {
                                    "min": {
                                        ElasticsearchQueryKeys.FIELD: SegmentKeys.START_TIME,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }

        response = await es.search(index=index, body=agg_query, ignore_unavailable=True)
        buckets = response[ElasticsearchKeys.AGGREGATIONS]["seasons"][ElasticsearchKeys.BUCKETS]

        total_segments = response[ElasticsearchKeys.HITS][ElasticsearchKeys.TOTAL][ElasticsearchAggregationKeys.VALUE]
        total_hours = 0.0
        total_episodes = 0
        total_seasons = len(buckets)

        for season_bucket in buckets:
            episode_buckets = season_bucket["episodes"][ElasticsearchKeys.BUCKETS]
            total_episodes += len(episode_buckets)
            for ep_bucket in episode_buckets:
                duration = ep_bucket["max_end"][ElasticsearchAggregationKeys.VALUE] - ep_bucket["min_start"][ElasticsearchAggregationKeys.VALUE]
                total_hours += max(0, duration)

        total_hours /= 3600

        return {
            "total_segments": total_segments,
            "total_episodes": total_episodes,
            "total_seasons": total_seasons,
            "total_hours": round(total_hours, 1),
        }
