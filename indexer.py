from elasticsearch import Elasticsearch, helpers
import json
import os
import git

# Użyj zmiennej środowiskowej dla adresu URL repozytorium
#REPO_URL = os.environ.get("REPO_URL")

es = Elasticsearch(["http://192.168.0.210:30003"])

# def clone_or_update_repo(repo_url, local_path="Ranczo-Transkrypcje"):
#     if os.path.exists(local_path):
#         print("Aktualizowanie repozytorium...")
#         repo = git.Repo(local_path)
#         origin = repo.remotes.origin
#         origin.pull()
#     else:
#         print("Klonowanie repozytorium...")
#         git.Repo.clone_from(repo_url, local_path)

def index_transcriptions(base_path="Ranczo-Transkrypcje"):
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        for episode_file in os.listdir(season_path):
            if episode_file.endswith(".json"):
                episode_video_path = episode_file.replace(".json", ".mp4")
                file_path = os.path.join(season_path, episode_file)
                with open(file_path, 'r') as file:
                    transcription = json.load(file)
                    for segment in transcription["segments"]:
                        segment["video_path"] = os.path.join("Ranczo-Wideo", season_dir, episode_video_path)
                        action = {
                            "_index": "ranczo-transcriptions",
                            "_source": segment
                        }
                        actions.append(action)
    helpers.bulk(es, actions)

if __name__ == "__main__":
    # if REPO_URL is None:
    #     print("Nie znaleziono URL repozytorium. Ustaw zmienną środowiskową REPO_URL.")
    # else:
    #     clone_or_update_repo(REPO_URL)
        index_transcriptions()
