import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from elasticsearch import Elasticsearch, helpers
import json
import os
import git
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv("passwords.env")

es_host = os.getenv("ES_HOST")
es_username = os.getenv("ES_USERNAME")
es_password = os.getenv("ES_PASSWORD")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

es = Elasticsearch(
    [es_host],
    basic_auth=(es_username, es_password),
    verify_certs=False,
)

def index_transcriptions(base_path="RANCZO-TRANSKRYPCJE"):
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):  # Dodaj tę linię
            for episode_file in os.listdir(season_path):
                if episode_file.endswith(".json"):
                    episode_video_path = episode_file.replace(".json", ".mp4")
                    file_path = os.path.join(season_path, episode_file)
                    with open(file_path, 'r') as file:
                        transcription = json.load(file)
                        for segment in transcription["segments"]:
                            segment["video_path"] = os.path.join("RANCZO-WIDEO", season_dir, episode_video_path)
                            action = {
                                "_index": "ranczo-transcriptions",
                                "_source": segment
                            }
                            actions.append(action)
    helpers.bulk(es, actions)

if __name__ == "__main__":
        index_transcriptions()
