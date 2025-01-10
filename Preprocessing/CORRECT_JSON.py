import argparse
import json
from pathlib import Path
from typing import (
    Dict,
    List,
)

DEFAULT_KEYS_TO_REMOVE = ["tokens", "no_speech_prob", "compression_ratio","avg_logprob","temperature"]

UNICODE_TO_POLISH_MAP = {
    '\\u0105': 'ą', '\\u0107': 'ć', '\\u0119': 'ę', '\\u0142': 'ł',
    '\\u0144': 'ń', '\\u00F3': 'ó', '\\u015B': 'ś', '\\u017A': 'ź',
    '\\u017C': 'ż', '\\u0104': 'Ą', '\\u0106': 'Ć', '\\u0118': 'Ę',
    '\\u0141': 'Ł', '\\u0143': 'Ń', '\\u00D3': 'Ó', '\\u015A': 'Ś',
    '\\u0179': 'Ź', '\\u017B': 'Ż',
}


def replace_unicode_chars(text: str) -> str:
    for unicode_char, char in UNICODE_TO_POLISH_MAP.items():
        text = text.replace(unicode_char, char)
    return text


def process_segment(segment: Dict[str, any], keys_to_remove: List[str]) -> Dict[str, any]:
    for key in keys_to_remove:
        segment.pop(key, None)

    segment["text"] = replace_unicode_chars(segment.get("text", ""))
    segment.update({
        "author": "",
        "comment": "",
        "tags": ["", ""],
        "location": "",
        "actors": ["", ""],
    })

    return segment


def process_json_file(file_path: Path, output_file_path: Path, keys_to_remove: List[str]) -> None:
    try:
        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)

        if "segments" in data:
            data["segments"] = [process_segment(segment, keys_to_remove) for segment in data["segments"]]

        with output_file_path.open('w', encoding='utf-8') as file:
            json.dump({"segments": data["segments"]}, file, ensure_ascii=False, indent=4)

        print(f"Processed file: {file_path}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def copy_and_process_hierarchy(input_folder: Path, output_folder: Path, keys_to_remove: List[str]) -> None:
    for item in input_folder.rglob('*'):
        relative_path = item.relative_to(input_folder)
        target_path = output_folder / relative_path

        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        elif item.is_file() and item.suffix == ".json":
            process_json_file(item, target_path, keys_to_remove)
        else:
            print(f"Skipping unsupported file: {item}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files recursively and remove specified keys.")
    parser.add_argument("--input-folder", required=True, type=str, help="Path to the folder containing JSON files.")
    parser.add_argument("--output-folder", required=True, type=str, help="Path to the folder where output will be saved.")
    parser.add_argument("--extra-keys-to-remove", type=str, nargs="*", default=[], help="Additional keys to remove.")

    args = parser.parse_args()
    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder)
    keys_to_remove = DEFAULT_KEYS_TO_REMOVE + args.extra_keys_to_remove

    if not input_folder.exists() or not input_folder.is_dir():
        print(f"Invalid input folder path: {input_folder}")
    else:
        output_folder.mkdir(parents=True, exist_ok=True)
        copy_and_process_hierarchy(input_folder, output_folder, keys_to_remove)
