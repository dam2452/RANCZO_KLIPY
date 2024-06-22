import logging
from elastic_manager import connect_to_elasticsearch

# Configure logging
logger = logging.getLogger(__name__)


def find_segment_by_quote(quote, season_filter=None, episode_filter=None, index='ranczo-transcriptions', return_all=False):
    logger.info(f"Searching for quote: '{quote}' with filters - Season: {season_filter}, Episode: {episode_filter}")
    es = connect_to_elasticsearch()
    query = {
        "query": {
            "match": {
                "text": {
                    "query": quote,
                    "fuzziness": "AUTO"
                }
            }
        }
    }

    size = 10000 if return_all else 1
    response = es.search(index=index, body=query, size=size)
    hits = response['hits']['hits']

    if not hits:
        logger.info("No segments found matching the query.")
        return None

    unique_segments = {}

    for hit in hits:
        segment = hit['_source']
        episode_info = segment.get('episode_info', {})
        title = episode_info.get('title', 'Unknown')
        season = episode_info.get('season', 'Unknown')
        episode_number = episode_info.get('episode_number', 'Unknown')

        unique_key = f"{title}-{season}-{episode_number}-{segment.get('start', 'Unknown')}"

        if unique_key not in unique_segments:
            unique_segments[unique_key] = segment

    logger.info(f"Found {len(unique_segments)} unique segments matching the query.")

    if return_all:
        return list(unique_segments.values())

    return next(iter(unique_segments.values()), None)