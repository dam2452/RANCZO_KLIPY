import json
import os


def load_episode_info():
    with open('EpisodeInfo.json', 'r', encoding='utf-8') as file:
        episode_info = json.load(file)
    return episode_info


def add_episode_info_to_transcriptions(base_path="RANCZO-TRANSKRYPCJE"):
    episode_info = load_episode_info()

    for season in range(1, 11):  # Dla 10 sezonów
        for episode in range(1, 14):  # Zakładając maksymalnie 13 odcinków na sezon
            episode_file_name = f"Ranczo_S{season:02d}E{episode:02d}.json"
            season_str = str(season)
            episodes_in_season = episode_info.get(season_str, [])

            if episode <= len(episodes_in_season):
                episode_info_data = episodes_in_season[episode - 1]

                transcriptions_path = os.path.join(base_path, f"Sezon {season}", episode_file_name)
                if os.path.exists(transcriptions_path):
                    with open(transcriptions_path, 'r', encoding='utf-8') as file:
                        transcriptions = json.load(file)

                    # Dodajemy informacje o sezonie do danych odcinka
                    episode_info_data_with_season = {
                        "season": season,  # Dodajemy numer sezonu
                        **episode_info_data
                    }

                    # Tworzymy nowy słownik z rozszerzonymi informacjami o odcinku na początku
                    updated_transcriptions = {
                        "episode_info": episode_info_data_with_season,
                        "segments": transcriptions.get("segments", [])
                    }

                    # Zapisujemy zmodyfikowane transkrypcje z powrotem do pliku
                    with open(transcriptions_path, 'w', encoding='utf-8') as file:
                        json.dump(updated_transcriptions, file, ensure_ascii=False, indent=4)
                    print(f"Updated: {transcriptions_path}")
                else:
                    print(f"File not found: {transcriptions_path}")
            else:
                print(f"No episode info available for Season {season}, Episode {episode}. Skipping...")


if __name__ == "__main__":
    add_episode_info_to_transcriptions()
