# Import statements organized alphabetically
from cachetools.func import ttl_cache
from elastic_manager import connect_to_elasticsearch  # Corrected import statement
import logging

logger = logging.getLogger(__name__)



# Decorator to cache results of the function, improving efficiency for repeated queries
def find_segment_by_quote(quote, season_filter=None, episode_filter=None, index='ranczo-transcriptions', return_all=False):
    # function body remains the same
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

    # Add a log to check the response from Elasticsearch
    logger.info(f"Elasticsearch response: {response}")

    if not hits:
        return None

    if return_all:
        return [hit['_source'] for hit in hits if all(key in hit['_source'] for key in ['video_path', 'start', 'end', 'episode_info'])]

    segment = hits[0]['_source']
    if all(key in segment for key in ['video_path', 'start', 'end', 'episode_info']):
        return segment
    else:
        # If 'episode_info' is not in the segment, create a default 'episode_info'
        segment['episode_info'] = {
            'episode_number': 0,
            'title': 'Unknown'
        }
        return segment