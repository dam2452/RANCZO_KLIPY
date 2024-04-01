# Standard library imports
import logging
# Third-party imports
from cachetools.func import ttl_cache
# Local application imports
from elastic_manager import connect_to_elasticsearch

# Configure logging
logger = logging.getLogger(__name__)

@ttl_cache(maxsize=1024, ttl=300)
def find_segment_by_quote(
    quote: str,
    season_filter: str = None,
    episode_filter: str = None,
    index: str = 'ranczo-transcriptions',
    return_all: bool = False
) -> dict:
    """
    Search for a segment by quote in an Elasticsearch index.

    Args:
    quote (str): The quote to search for.
    season_filter (str, optional): Season to filter the results. Defaults to None.
    episode_filter (str, optional): Episode to filter the results. Defaults to None.
    index (str, optional): The Elasticsearch index to search in. Defaults to 'ranczo-transcriptions'.
    return_all (bool, optional): If True, returns all results, else returns the first. Defaults to False.

    Returns:
    dict: The found segment or segments.
    """
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
        return None

    unique_segments = {}  # Tracks unique segments to avoid duplicates

    for hit in hits:
        segment = hit['_source']
        if all(key in segment for key in ['video_path', 'start', 'end', 'episode_info']):
            # Creating a unique identifier for each segment
            unique_key = f"{segment['episode_info']['title']}-{segment['start']}"
            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment

    if return_all:
        return list(unique_segments.values())

    if unique_segments:
        # Return the first segment if not returning all
        return next(iter(unique_segments.values()))

    # Return None if no segments are found
    return None
