import logging
from elasticsearch import AsyncElasticsearch
from bot.elastic_manager import connect_to_elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_segment_by_quote(quote, season_filter=None, episode_filter=None, index='ranczo-transcriptions', return_all=False):
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
    logger.info(f"Searching for quote: '{quote}' with filters - Season: {season_filter}, Episode: {episode_filter}")
    es = await connect_to_elasticsearch()

    if not es:
        logger.error("Failed to connect to Elasticsearch.")
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
        query["query"]["bool"]["filter"].append({"term": {"episode_info.episode_number": episode_filter}}) #Globl number of episode

    size = 10000 if return_all else 1

    try:
        response = await es.search(index=index, body=query, size=size)
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
            start_time = segment.get('start', 'Unknown')

            unique_key = f"{title}-{season}-{episode_number}-{start_time}"

            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment

        logger.info(f"Found {len(unique_segments)} unique segments matching the query.")

        if return_all:
            return list(unique_segments.values())

        return next(iter(unique_segments.values()), None)

    except Exception as e:
        logger.error(f"An error occurred while searching for segments: {e}")
        return None

