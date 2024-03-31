# cat indexer.py
import urllib3
import logging
from elasticsearch import Elasticsearch, helpers
import json
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv("passwords.env")

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wyłączenie ostrzeżenia dotyczącego niezaufanych żądań HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

es = Elasticsearch(
    [es_host],
    basic_auth=(es_username, es_password),
    verify_certs=False,
)

def index_transcriptions(base_path="RANCZO-TRANSKRYPCJE"):
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith(".json"):
                    episode_video_path = episode_file.replace(".json", ".mp4")
                    file_path = os.path.join(season_path, episode_file)
                    logger.info(f"Indexing transcription from: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as file:
                        transcription = json.load(file)
                        for segment in transcription["segments"]:
                            segment["video_path"] = os.path.join("RANCZO-WIDEO", season_dir, episode_video_path)
                            actions.append({
                                "_index": "ranczo-transcriptions",
                                "_source": segment
                            })
    logger.info("Bulk indexing transcriptions...")
    helpers.bulk(es, actions)
    logger.info("Transcriptions indexed successfully.")

def delete_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

if __name__ == "__main__":
    delete_index("ranczo-transcriptions")
    index_transcriptions()