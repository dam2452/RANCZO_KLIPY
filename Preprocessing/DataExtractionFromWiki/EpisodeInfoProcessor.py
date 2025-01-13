import argparse
import json
from pathlib import Path
import re
import sys
from typing import (
    Any,
    Dict,
    Optional,
)

from Preprocessing.ErrorLogger import ErrorLogger
from Preprocessing.utils import setup_logger


class EpisodeInfoProcessor:
    def __init__(self, base_path: str, episode_info_path: str, output_path: str):
        self.base_path = Path(base_path)
        self.episode_info_path = Path(episode_info_path)
        self.output_path = Path(output_path)
        self.logger = setup_logger(self.__class__.__name__)
        self.error_logger = ErrorLogger(self.logger)

    def load_episode_info(self) -> Dict[str, Any]:
        try:
            with self.episode_info_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as exc:
            self.error_logger.log_error(f"Episode info file not found: {self.episode_info_path}")
            raise ValueError(f"Episode info file not found: {self.episode_info_path}") from exc
        except json.JSONDecodeError as exc:
            self.error_logger.log_error(f"Error decoding JSON in episode info file {self.episode_info_path}: {exc}")
            raise ValueError(f"Error decoding JSON in episode info file {self.episode_info_path}: {exc}") from exc

    @staticmethod
    def parse_episode_info(file_name: str) -> Optional[int]:
        pattern = r"E(?P<episode>\d{3})"
        match = re.search(pattern, file_name, re.IGNORECASE)
        if match:
            return int(match.group("episode"))
        return None

    @staticmethod
    def find_episode_info(episode_info: Dict[str, Any], episode_number: int) -> Optional[Dict[str, Any]]:
        for season_str, data in episode_info.items():
            episodes = data.get("episodes", [])
            for ep_data in episodes:
                if ep_data.get("episode_number") == episode_number:
                    return {
                        "season": int(season_str),
                        "episode_number": ep_data.get("episode_number"),
                        "premiere_date": ep_data.get("premiere_date"),
                        "title": ep_data.get("title"),
                        "viewership": ep_data.get("viewership"),
                    }
        return None

    def process_file(self, file_path: Path, episode_info: Dict[str, Any]) -> None:
        relative_path = file_path.relative_to(self.base_path)
        output_file_path = self.output_path / relative_path

        episode_number = self.parse_episode_info(file_path.name)
        if not episode_number:
            self.error_logger.log_error(f"Filename does not match episode pattern: {file_path.name}")
            return

        episode_info_data = self.find_episode_info(episode_info, episode_number)
        if not episode_info_data:
            self.error_logger.log_error(f"No episode info for Episode {episode_number}. Skipping...")
            return

        try:
            with file_path.open("r", encoding="utf-8") as file:
                transcriptions = json.load(file)

            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            updated_transcriptions = {
                "episode_info": episode_info_data,
                "segments": transcriptions.get("segments", []),
            }

            with output_file_path.open("w", encoding="utf-8") as file:
                json.dump(updated_transcriptions, file, ensure_ascii=False, indent=4)

            self.logger.info(f"Created file: {output_file_path}")

        except FileNotFoundError:
            self.error_logger.log_error(f"File not found: {file_path}")
        except json.JSONDecodeError as exc:
            self.error_logger.log_error(f"Error decoding JSON in file {file_path}: {exc}")
        except PermissionError:
            self.error_logger.log_error(f"Permission denied when accessing file: {file_path}")

    def run(self) -> int:
        try:
            episode_info = self.load_episode_info()
        except ValueError as e:
            self.logger.error(e)
            return 2

        if not self.base_path.is_dir():
            self.error_logger.log_error(f"Invalid base path: {self.base_path}")
            return 2

        for file_path in self.base_path.rglob("*.json"):
            self.process_file(file_path, episode_info)

        return self.error_logger.finalize()


def main():
    parser = argparse.ArgumentParser(description="Add episode info (including 'season') to transcription files.")
    parser.add_argument("--base-path", required=True, type=str, help="Base path to transcription files.")
    parser.add_argument("--episode-info-path", required=True, type=str, help="Path to the EpisodeInfo.json file.")
    parser.add_argument("--output-path", required=True, type=str, help="Path for the modified transcription files.")

    args = parser.parse_args()

    processor = EpisodeInfoProcessor(args.base_path, args.episode_info_path, args.output_path)
    exit_code = processor.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
