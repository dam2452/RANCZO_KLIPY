# Import statements organized alphabetically
from cachetools.func import ttl_cache
from elastic_manager import connect_to_elasticsearch  # Corrected import statement


# Decorator to cache results of the function, improving efficiency for repeated queries
@ttl_cache(maxsize=100, ttl=3600)
def find_segment_by_quote(quote, index='ranczo-transcriptions'):
    """
    Search for a segment by quote in the given index.

    Args:
    quote (str): The quote to search for.
    index (str, optional): The Elasticsearch index to search in. Defaults to 'ranczo-transcriptions'.

    Returns:
    dict or None: The first segment containing the quote if found, else None.
    """
    # Establish connection to Elasticsearch
    es = connect_to_elasticsearch()  # Corrected function call

    # Define the search query with fuzziness to account for minor typos or variations
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

    # Execute the search query
    response = es.search(index=index, body=query)
    hits = response['hits']['hits']

    # Return None if no hits are found
    if not hits:
        return None

    # Extract the segment information from the first hit
    segment = hits[0]['_source']

    # Check if the segment contains required keys ('video_path', 'start', 'end')
    # and return the segment if it does, otherwise return None
    if all(key in segment for key in ['video_path', 'start', 'end']):
        return segment

    return None