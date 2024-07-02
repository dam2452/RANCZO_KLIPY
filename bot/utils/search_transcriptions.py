import logging
from bot.utils.elastic_manager import connect_to_elasticsearch
from bot.middlewares.authorization import AuthorizationMiddleware
from bot.middlewares.error_handler import ErrorHandlerMiddleware
from aiogram import Dispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchTranscriptions:
    def __init__(self, dispatcher: Dispatcher):
        dispatcher.message.middleware(AuthorizationMiddleware())
        dispatcher.message.middleware(ErrorHandlerMiddleware())

    async def find_segment_by_quote(self, quote, season_filter=None, episode_filter=None, index='ranczo-transcriptions',
                                    return_all=False):
        """
        Searches for a segment by a given quote with optional season and episode filters.

        Parameters:
        - quote: The text to search for within segments.
        - season_filter: Optional filter to narrow down results to a specific season.
        - episode_filter: Optional filter to narrow down results to a specific episode.
        - index: The Elasticsearch index to search within.
        - return_all: If True, returns all matching segments; otherwise, returns the first match.

        Returns:
        - A list of matching segments if return_all is True.
        - The first matching segment if return_all is False.
        - None if no matches are found.
        """
        logger.info(
            f"🔍 Searching for quote: '{quote}' with filters - Season: {season_filter}, Episode: {episode_filter}")
        es = await connect_to_elasticsearch()

        if not es:
            logger.error("❌ Failed to connect to Elasticsearch.❌")
            return None

        # Construct the base query
        query = {
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "text": {
                                "query": quote,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    "filter": []
                }
            }
        }

        # Add season filter if provided
        if season_filter:
            query["query"]["bool"]["filter"].append({"term": {"episode_info.season": season_filter}})

        # Add episode filter if provided
        if episode_filter:
            query["query"]["bool"]["filter"].append(
                {"term": {"episode_info.episode_number": episode_filter}})  # Global number of episode

        size = 10000 if return_all else 1

        try:
            response = await es.search(index=index, body=query, size=size)
            hits = response['hits']['hits']

            if not hits:
                logger.info("❌ No segments found matching the query.❌")
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

            logger.info(f"✅ Found {len(unique_segments)} unique segments matching the query.✅")

            if return_all:
                return list(unique_segments.values())

            return next(iter(unique_segments.values()), None)

        except Exception as e:
            logger.error(f"❌ An error occurred while searching for segments: {e}❌")
            return None

    async def find_segment_with_context(self, quote, context_size=30, season_filter=None, episode_filter=None,
                                        index='ranczo-transcriptions'):
        logger.info(
            f"🔍 Searching for quote: '{quote}' with context size: {context_size}, filters - Season: {season_filter}, Episode: {episode_filter}")
        es = await connect_to_elasticsearch()

        if not es:
            logger.error("❌ Failed to connect to Elasticsearch.❌")
            return None

        segment = await self.find_segment_by_quote(quote, season_filter, episode_filter, index, return_all=False)
        if not segment:
            logger.info("❌ No segments found matching the query.❌")
            return None

        segment = segment[0] if isinstance(segment, list) else segment
        segment_id = segment['id']
        episode_number = segment['episode_info']['episode_number']
        season_number = segment['episode_info']['season']

        context_query_before = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"episode_info.season": season_number}},
                        {"term": {"episode_info.episode_number": episode_number}}
                    ],
                    "filter": [
                        {"range": {"id": {"lt": segment_id}}}
                    ]
                }
            },
            "sort": [{"id": "desc"}],
            "size": context_size
        }

        context_query_after = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"episode_info.season": season_number}},
                        {"term": {"episode_info.episode_number": episode_number}}
                    ],
                    "filter": [
                        {"range": {"id": {"gt": segment_id}}}
                    ]
                }
            },
            "sort": [{"id": "asc"}],
            "size": context_size
        }

        try:
            context_response_before = await es.search(index=index, body=context_query_before)
            context_response_after = await es.search(index=index, body=context_query_after)

            context_segments_before = [{'id': hit['_source']['id'], 'text': hit['_source']['text']} for hit in
                                       context_response_before['hits']['hits']]
            context_segments_after = [{'id': hit['_source']['id'], 'text': hit['_source']['text']} for hit in
                                      context_response_after['hits']['hits']]

            context_segments_before.reverse()

            context_segments = context_segments_before + [
                {'id': segment['id'], 'text': segment['text']}] + context_segments_after

            seen_ids = set()
            unique_context_segments = []
            for seg in context_segments:
                if seg['id'] not in seen_ids:
                    unique_context_segments.append(seg)
                    seen_ids.add(seg['id'])

            logger.info(f"✅ Found {len(unique_context_segments)} unique segments for context.✅")

            target_index = unique_context_segments.index({'id': segment['id'], 'text': segment['text']})
            start_index = max(target_index - context_size, 0)
            end_index = min(target_index + context_size + 1, len(unique_context_segments))
            final_context_segments = unique_context_segments[start_index:end_index]

            return {
                "target": segment,
                "context": final_context_segments
            }

        except Exception as e:
            logger.error(f"❌ An error occurred while searching for segment with context: {e} ❌")
            return None
