import json
import logging
from typing import (
    List,
    Optional,
    Union,
)

from elastic_transport import ObjectApiResponse

from bot.search.elastic_search import connect_to_elasticsearch
from bot.utils.log import log_system_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionFinder:
    @staticmethod
    async def find_segment_by_quote(
            quote: str, season_filter: Optional[int] = None, episode_filter: Optional[int] = None,
            index: str = 'ranczo-transcriptions', return_all: bool = False,
    ) -> Optional[Union[List[ObjectApiResponse], ObjectApiResponse]]:
        await log_system_message(
            logging.INFO,
            f"Searching for quote: '{quote}' with filters - Season: {season_filter}, Episode: {episode_filter}",
            logger,
        )
        es = await connect_to_elasticsearch()

        query = {
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "text": {
                                "query": quote,
                                "fuzziness": "AUTO",
                            },
                        },
                    },
                    "filter": [],
                },
            },
        }

        if season_filter:
            query["query"]["bool"]["filter"].append({"term": {"episode_info.season": season_filter}})

        if episode_filter:
            query["query"]["bool"]["filter"].append({"term": {"episode_info.episode_number": episode_filter}})

        size = 10000 if return_all else 1

        response = await es.search(index=index, body=query, size=size)
        hits = response['hits']['hits']

        if not hits:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        unique_segments = {}

        for hit in hits:
            segment = hit['_source']
            episode_info = segment.get('episode_info', {})
            title = episode_info.get('title', 'Unknown')
            season = episode_info.get('season', 'Unknown')
            episode_number = episode_info.get('episode_number', 'Unknown')
            start_time = segment.get('start', 'Unknown')

            unique_key = f"{title}-{season}-{episode_number}-{start_time}"

            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment

        await log_system_message(logging.INFO, f"Found {len(unique_segments)} unique segments matching the query.", logger)

        if return_all:
            return list(unique_segments.values())

        return next(iter(unique_segments.values()), None)

    @staticmethod
    async def find_segment_with_context(
            quote: str, context_size: int = 30, season_filter: Optional[str] = None, episode_filter: Optional[str] = None,
            index: str = 'ranczo-transcriptions',
    ) -> Optional[json]:
        await log_system_message(
            logging.INFO,
            f"🔍 Searching for quote: '{quote}' with context size: {context_size}. Season: {season_filter}, Episode: {episode_filter}",
            logger,
        )
        es = await connect_to_elasticsearch()

        segment = await TranscriptionFinder.find_segment_by_quote(quote, season_filter, episode_filter, index, return_all=False)
        if not segment:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        segment = segment[0] if isinstance(segment, list) else segment

        context_query_before = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"episode_info.season": segment['episode_info']['season']}},
                        {"term": {"episode_info.episode_number": segment['episode_info']['episode_number']}},
                    ],
                    "filter": [
                        {"range": {"id": {"lt": segment['id']}}},
                    ],
                },
            },
            "sort": [{"id": "desc"}],
            "size": context_size,
        }

        context_query_after = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"episode_info.season": segment['episode_info']['season']}},
                        {"term": {"episode_info.episode_number": segment['episode_info']['episode_number']}},
                    ],
                    "filter": [
                        {"range": {"id": {"gt": segment['id']}}},
                    ],
                },
            },
            "sort": [{"id": "asc"}],
            "size": context_size,
        }

        context_response_before = await es.search(index=index, body=context_query_before)
        context_response_after = await es.search(index=index, body=context_query_after)

        context_segments_before = [{'id': hit['_source']['id'], 'text': hit['_source']['text']} for hit in
                                   context_response_before['hits']['hits']]
        context_segments_after = [{'id': hit['_source']['id'], 'text': hit['_source']['text']} for hit in
                                  context_response_after['hits']['hits']]

        context_segments_before.reverse()

        unique_context_segments = []
        for seg in context_segments_before + [{'id': segment['id'], 'text': segment['text']}] + context_segments_after:
            if seg not in unique_context_segments:
                unique_context_segments.append(seg)

        await log_system_message(logging.INFO, f"Found {len(unique_context_segments)} unique segments for context.", logger)

        target_index = unique_context_segments.index({'id': segment['id'], 'text': segment['text']})
        start_index = max(target_index - context_size, 0)
        end_index = min(target_index + context_size + 1, len(unique_context_segments))

        return {"target": segment, "context": unique_context_segments[start_index:end_index]}

    @staticmethod
    async def find_video_path_by_episode(season: int, episode_number: int, index: str = 'ranczo-transcriptions') -> Optional[str]:
        await log_system_message(
            logging.INFO,
            f"Searching for video path with filters - Season: {season}, Episode: {episode_number}",
            logger,
        )
        es = await connect_to_elasticsearch()

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"episode_info.season": season}},
                        {"term": {"episode_info.episode_number": episode_number}},
                    ],
                },
            },
        }

        response = await es.search(index=index, body=query, size=1)
        hits = response['hits']['hits']

        if not hits:
            await log_system_message(logging.INFO, "No segments found matching the query.", logger)
            return None

        segment = hits[0]['_source']
        video_path = segment.get('video_path', None)

        if video_path:
            await log_system_message(logging.INFO, f"Found video path: {video_path}", logger)
            return video_path

        await log_system_message(logging.INFO, "Video path not found in the segment.", logger)
        return None

    @staticmethod
    async def find_episodes_by_season(season: int, index: str = 'ranczo-transcriptions') -> Optional[List[json]]:
        await log_system_message(logging.INFO, f"Searching for episodes in season {season}", logger)
        es = await connect_to_elasticsearch()

        query = {
            "size": 0,
            "query": {
                "term": {"episode_info.season": season},
            },
            "aggs": {
                "unique_episodes": {
                    "terms": {
                        "field": "episode_info.episode_number",
                        "size": 1000,
                        "order": {
                            "_key": "asc",
                        },
                    },
                    "aggs": {
                        "episode_info": {
                            "top_hits": {
                                "size": 1,
                                "_source": {
                                    "includes": [
                                        "episode_info.title",
                                        "episode_info.premiere_date",
                                        "episode_info.viewership",
                                        "episode_info.episode_number",
                                    ],
                                },
                            },
                        },
                    },
                },
            },
        }

        response = await es.search(index=index, body=query)
        buckets = response['aggregations']['unique_episodes']['buckets']

        if not buckets:
            await log_system_message(logging.INFO, f"No episodes found for season {season}.", logger)
            return None

        episodes = []
        for bucket in buckets:
            episode_info = bucket['episode_info']['hits']['hits'][0]['_source']['episode_info']
            episode = {
                "episode_number": episode_info.get('episode_number'),
                "title": episode_info.get('title', 'Unknown'),
                "premiere_date": episode_info.get('premiere_date', 'Unknown'),
                "viewership": episode_info.get('viewership', 'Unknown'),
            }
            episodes.append(episode)

        await log_system_message(logging.INFO, f"Found {len(episodes)} episodes for season {season}.", logger)
        return episodes
