import json
import logging
import os
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch, helpers
import urllib3


# Configure basic logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable warnings regarding untrusted HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



load_dotenv("../.env")

# Retrieve environment variables
es_host = os.getenv("ES_HOST")
print(es_host)
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
# Additional variable for Telegram bot token, if needed
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

async def connect_to_elasticsearch():
    """
    Establishes a connection to Elasticsearch.
    """
    try:
        es = AsyncElasticsearch(
            [es_host],
            http_auth=(es_username, es_password),
            verify_certs=False,  # Set to True in production for security
        )
        if not await es.ping():
            raise ValueError("Failed to connect to Elasticsearch.")
        logger.info("Connected to Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Connection to Elasticsearch failed: {e}")
        return None

async def delete_all_indices(es):
    """
    Deletes all indices in Elasticsearch.
    """
    try:
        all_indices = await es.indices.get_alias(name="*")
        if not all_indices:
            logger.info("No indices to delete.")
            return

        for index in all_indices:
            await es.indices.delete(index=index)
            logger.info(f"Deleted index: {index}")
        logger.info("All indices have been deleted.")
    except Exception as e:
        logger.error(f"Error deleting indices: {e}")

async def index_transcriptions(base_path, es):
    """
    Indexes transcription files from the given base path.
    """
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith('.json'):
                    file_path = os.path.join(season_path, episode_file)
                    logger.info(f"Processing file: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        episode_info = data.get('episode_info', {})

                        # Correct 'video_path' to match Linux format
                        video_path = os.path.join("RANCZO-WIDEO", season_dir, episode_file.replace('.json', '.mp4'))
                        video_path = video_path.replace("\\", os.path.sep)  # Ensure correct separators

                        for segment in data.get('segments', []):
                            segment['episode_info'] = episode_info
                            segment['video_path'] = video_path  # Add video path

                            actions.append({
                                "_index": "ranczo-transcriptions",
                                "_source": segment
                            })

    if actions:
        logger.info(f"Indexing {len(actions)} segments.")
        await helpers.async_bulk(es, actions)
        logger.info("Data indexed successfully.")
    else:
        logger.info("No data to index.")

async def print_one_transcription(es, index="ranczo-transcriptions"):
    """
    Prints one transcription document from Elasticsearch.
    """
    try:
        response = await es.search(index=index, size=1)
        if response['hits']['hits']:
            document = response['hits']['hits'][0]['_source']
            logger.info("Retrieved document:")
            print(json.dumps(document, indent=4, ensure_ascii=False))
        else:
            logger.info("No documents found.")
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")

if __name__ == "__main__":
    import asyncio

    async def main():
        es_client = await connect_to_elasticsearch()
        if es_client:
            # Uncomment the following line if you need to delete all indices before indexing
            # await delete_all_indices(es_client)
            # await index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=es_client)
            # Print one transcription document
            await print_one_transcription(es_client)

    asyncio.run(main())
