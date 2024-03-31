import os
import logging
import urllib3
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import json
import warnings

# Załaduj zmienne środowiskowe z pliku .env, jeśli istnieje
env_file = os.path.join(os.getcwd(), "passwords.env")  # Ulepszona ścieżka
if os.path.exists(env_file):
    load_dotenv(env_file)

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wyłączenie ostrzeżenia dotyczącego niezaufanych żądań HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect_elastic():
    """
    Funkcja do nawiązywania połączenia z Elasticsearch.
    """
    try:
        es = Elasticsearch(
            [es_host],
            http_auth=(es_username, es_password),
            verify_certs=False,  # Na potrzeby testów, w produkcji należy włączyć
        )
        if not es.ping():
            raise ValueError("Połączenie z Elasticsearch nie powiodło się.")
        logger.info("Połączono z Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Nie udało się połączyć z Elasticsearch: {e}")
        return None

def clear_all_indices(es):
    """
    Usuwa wszystkie indeksy w Elasticsearch.
    """
    try:
        if not es.ping():
            logger.error("Nie udało się połączyć z Elasticsearch.")
            return

        all_indices = es.indices.get_alias("*")
        for index in all_indices:
            es.indices.delete(index=index)
            logger.info(f"Usunięto indeks: {index}")
        logger.info("Wszystkie indeksy zostały usunięte.")
    except Exception as e:
        warnings.warn(f"Wystąpił problem podczas usuwania indeksów: {e}")

def index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=None):
    if es is None:
        es = connect_elastic()

    base_path = os.path.join(os.getcwd(), base_path)  # Ulepszona ścieżka
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
                            segment["video_path"] = episode_video_path  # Ulepszona ścieżka
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

# Użycie
es_client = connect_elastic()
if es_client:
    clear_all_indices(es_client)
    index_transcriptions(base_path="RANCZO-TRANSKRYPCJE", es=es_client)
