import argparse
import json
from pathlib import Path
import sys
from typing import (
    List,
)

from Preprocessing.ErrorLogger import ErrorLogger
from Preprocessing.utils import setup_logger


class JSONProcessor:
    DEFAULT_KEYS_TO_REMOVE = ["tokens", "no_speech_prob", "compression_ratio", "avg_logprob", "temperature"]
    UNICODE_TO_POLISH_MAP = {
        '\\u0105': 'ą', '\\u0107': 'ć', '\\u0119': 'ę', '\\u0142': 'ł',
        '\\u0144': 'ń', '\\u00F3': 'ó', '\\u015B': 'ś', '\\u017A': 'ź',
        '\\u017C': 'ż', '\\u0104': 'Ą', '\\u0106': 'Ć', '\\u0118': 'Ę',
        '\\u0141': 'Ł', '\\u0143': 'Ń', '\\u00D3': 'Ó', '\\u015A': 'Ś',
        '\\u0179': 'Ź', '\\u017B': 'Ż',
    }

    def __init__(self, input_folder: str, output_folder: str, extra_keys_to_remove: List[str]):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.keys_to_remove = self.DEFAULT_KEYS_TO_REMOVE + extra_keys_to_remove
        self.logger = setup_logger(self.__class__.__name__)
        self.error_logger = ErrorLogger(self.logger)

    @staticmethod
    def replace_unicode_chars(text: str) -> str:
        for unicode_char, char in JSONProcessor.UNICODE_TO_POLISH_MAP.items():
            text = text.replace(unicode_char, char)
        return text

    def process_segment(self, segment: json) -> json:
        for key in self.keys_to_remove:
            segment.pop(key, None)

        segment["text"] = self.replace_unicode_chars(segment.get("text", ""))
        segment.update({
            "author": "",
            "comment": "",
            "tags": ["", ""],
            "location": "",
            "actors": ["", ""],
        })

        return segment

    def process_json_file(self, file_path: Path, output_file_path: Path) -> None:
        try:
            with file_path.open('r', encoding='utf-8') as file:
                data = json.load(file)

            if "segments" in data:
                data["segments"] = [self.process_segment(segment) for segment in data["segments"]]

            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with output_file_path.open('w', encoding='utf-8') as file:
                json.dump({"segments": data["segments"]}, file, ensure_ascii=False, indent=4)

            self.logger.info(f"Processed file: {file_path}")

        except FileNotFoundError:
            self.error_logger.log_error(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            self.error_logger.log_error(f"JSON decoding error in file {file_path}: {e}")
        except PermissionError:
            self.error_logger.log_error(f"Permission error while accessing file: {file_path}")

    def copy_and_process_hierarchy(self) -> None:
        for item in self.input_folder.rglob('*'):
            relative_path = item.relative_to(self.input_folder)
            target_path = self.output_folder / relative_path

            if item.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            elif item.is_file() and item.suffix == ".json":
                self.process_json_file(item, target_path)
            else:
                self.logger.warning(f"Skipping unsupported file: {item}")

    def run(self) -> int:
        if not self.input_folder.exists() or not self.input_folder.is_dir():
            self.error_logger.log_error(f"Invalid input folder path: {self.input_folder}")
            return 2

        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.copy_and_process_hierarchy()
        return self.error_logger.finalize()


def main() -> None:
    parser = argparse.ArgumentParser(description="Process JSON files recursively and remove specified keys.")
    parser.add_argument("--input-folder", required=True, type=str, help="Path to the folder containing JSON files.")
    parser.add_argument("--output-folder", required=True, type=str, help="Path to the folder where output will be saved.")
    parser.add_argument("--extra-keys-to-remove", type=str, nargs="*", default=[], help="Additional keys to remove.")

    args = parser.parse_args()

    processor = JSONProcessor(args.input_folder, args.output_folder, args.extra_keys_to_remove)
    exit_code = processor.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
