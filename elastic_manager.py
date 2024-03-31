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
        if not es.ping():
            logger.error("Failed to connect to Elasticsearch.")
            return

        all_indices = es.indices.get_alias("*")
        for index in all_indices:
            es.indices.delete(index=index)
            logger.info(f"Deleted index: {index}")
        logger.info("All indices have been deleted.")
    except Exception as e:
        logger.error(f"Error deleting indices: {e}")

def index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=None):
    """
    Indexes transcriptions into Elasticsearch.
    """
    if es is None:
        es = connect_to_elasticsearch()
        if es is None:
            return

    base_path = os.path.join(os.getcwd(), base_path)
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith(".json"):
                    episode_video_path = os.path.join("RANCZO-WIDEO", season_dir, episode_file.replace(".json", ".mp4"))
                    file_path = os.path.join(season_path, episode_file)
                    logger.info(f"Indexing transcription from: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as file:
                        transcription = json.load(file)
                        episode_info = transcription.get("episode_info", {})
                        for segment in transcription.get("segments", []):
                            segment["video_path"] = episode_video_path
                            segment["episode_info"] = episode_info
                            actions.append({
                                "_index": "ranczo-transcriptions",
                                "_source": segment
                            })
    if actions:
        logger.info("Bulk indexing transcriptions...")
        helpers.bulk(es, actions)
        logger.info("Transcriptions indexed successfully.")
    else:
        logger.info("No transcriptions found to index.")

if __name__ == "__main__":
    es_client = connect_to_elasticsearch()
    if es_client:
        delete_all_indices(es_client)
        index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=es_client)
