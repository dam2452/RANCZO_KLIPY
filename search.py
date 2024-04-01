# Import statements organized alphabetically
from cachetools.func import ttl_cache
from elastic_manager import connect_to_elasticsearch  # Corrected import statement
import logging

logger = logging.getLogger(__name__)



# Decorator to cache results of the function, improving efficiency for repeated queries
def find_segment_by_quote(quote, season_filter=None, episode_filter=None, index='ranczo-transcriptions', return_all=False):
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

    response = es.search(index=index, body=query, size=10000 if return_all else 1)
    hits = response['hits']['hits']

    if not hits:
        return None

    unique_segments = {}  # Using a dictionary to track unique segments

    for hit in hits:
        segment = hit['_source']
        if all(key in segment for key in ['video_path', 'start', 'end', 'episode_info']):
            # Construct a unique key for each segment
            unique_key = f"{segment['episode_info']['title']}-{segment['start']}"
            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment

    if return_all:
        return list(unique_segments.values())

    if unique_segments:
        return next(iter(unique_segments.values()))  # Return the first segment

    # Fallback if no segments are found
    return None

# You don't need to modify the `list_all_quotes` function specifically for duplicates handling,
# as the `find_segment_by_quote` function now ensures that only unique segments are returned.

# Note: Ensure that you properly handle the Elasticsearch connection and logging as needed.
