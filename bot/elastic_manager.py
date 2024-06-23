import json
import logging
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
import urllib3

# Configure basic logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable warnings regarding untrusted HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file, if it exists
env_file = os.path.join(os.getcwd(), "passwords.env")
if os.path.exists(env_file):
    load_dotenv(env_file)

# Retrieve environment variables
es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
# Additional variable for Telegram bot token, if needed
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")


def connect_to_elasticsearch():
    """
    Establishes a connection to Elasticsearch.
    """
    try:
        es = Elasticsearch(
            [es_host],
            http_auth=(es_username, es_password),
            verify_certs=False,  # Set to True in production for security
        )
        if not es.ping():
            raise ValueError("Failed to connect to Elasticsearch.")
        logger.info("Connected to Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Connection to Elasticsearch failed: {e}")
        return None


def delete_all_indices(es):
    """
    Deletes all indices in Elasticsearch.
    """
    try:
        all_indices = es.indices.get_alias(name="*")
        if not all_indices:
            logger.info("No indices to delete.")
            return

        for index in all_indices:
            es.indices.delete(index=index)
            logger.info(f"Deleted index: {index}")
        logger.info("All indices have been deleted.")
    except Exception as e:
        logger.error(f"Error deleting indices: {e}")


def index_transcriptions(base_path, es):
    """
    Indexes transcription files from the given base path into Elasticsearch.
    """
    logger.info(f"Starting to index transcriptions from base path: {base_path}")
    actions = []

    for season_dir in sorted(os.listdir(base_path)):
        season_path = os.path.join(base_path, season_dir)
        if not os.path.isdir(season_path):
            logger.warning(f"Skipping non-directory: {season_path}")
            continue

        logger.info(f"Processing season directory: {season_path}")

        for episode_file in sorted(os.listdir(season_path)):
            if not episode_file.endswith('.json'):
                logger.warning(f"Skipping non-JSON file: {episode_file}")
                continue

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
        helpers.bulk(es, actions)
        logger.info("Data indexed successfully.")
    else:
        logger.info("No data to index.")

def print_one_transcription(es, index="ranczo-transcriptions"):
    """
    Prints one transcription document from Elasticsearch.
    """
    try:
        response = es.search(index=index, size=1)
        if response['hits']['hits']:
            document = response['hits']['hits'][0]['_source']
            logger.info("Retrieved document:")
            print(json.dumps(document, indent=4, ensure_ascii=False))
        else:
            logger.info("No documents found.")
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")

if __name__ == "__main__":
    es_client = connect_to_elasticsearch()
    if es_client:
        #Uncomment the following line if you need to delete all indices before indexing
        #delete_all_indices(es_client)
        #index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=es_client)
        # Print one transcription document
        print_one_transcription(es_client)