import json
import logging
import os


def load_episode_info() -> json:
    with open('EpisodeInfo.json', 'r', encoding='utf-8') as file:
        episode_info = json.load(file)
    return episode_info


def add_episode_info_to_transcriptions(base_path: str = "RANCZO-TRANSKRYPCJE") -> None:
    episode_info = load_episode_info()

    for season in range(1, 11):
        for episode in range(1, 14):
            episode_file_name = f"Ranczo_S{season:02d}E{episode:02d}.json"
            season_str = str(season)
            episodes_in_season = episode_info.get(season_str, [])

            if episode <= len(episodes_in_season):
                episode_info_data = episodes_in_season[episode - 1]

                transcriptions_path = os.path.join(base_path, f"Sezon {season}", episode_file_name)
                if os.path.exists(transcriptions_path):
                    with open(transcriptions_path, 'r', encoding='utf-8') as file:
                        transcriptions = json.load(file)

                    episode_info_data_with_season = {
                        "season": season,
                        **episode_info_data,
                    }

                    updated_transcriptions = {
                        "episode_info": episode_info_data_with_season,
                        "segments": transcriptions.get("segments", []),
                    }

                    with open(transcriptions_path, 'w', encoding='utf-8') as file:
                        json.dump(updated_transcriptions, file, ensure_ascii=False, indent=4)
                    logging.info(f"Updated: {transcriptions_path}")
                else:
                    logging.error(f"File not found: {transcriptions_path}")
            else:
                logging.error(f"No episode info available for Season {season}, Episode {episode}. Skipping...")


if __name__ == "__main__":
    add_episode_info_to_transcriptions()
