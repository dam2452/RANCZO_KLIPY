import argparse
import os
from pathlib import Path
import subprocess


def process_audio_files(input_folder: str, output_folder: str, model: str = "large-v3", language: str = "Polish", device: str = "cuda") -> None:
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)

    for file_path in input_folder.rglob("*"):
        if file_path.suffix.lower() in [".wav", ".mp3"]:
            relative_path = file_path.relative_to(input_folder)
            output_path = output_folder / relative_path.with_suffix("_processed.wav")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                subprocess.run(
                    [
                        "whisper", str(file_path), "--model", model, "--language", language, "--device", device,
                        "--output_dir", str(output_path.parent),
                    ],
                    check=True,
                )
                print(f"Processed: {file_path} -> {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file_path}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Process .wav and .mp3 files using Whisper model.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder")
    parser.add_argument("output_folder", type=str, help="Path to the output folder")
    parser.add_argument("--model", type=str, default="large-v3", help="Whisper model to use (default: 'large-v3')")
    parser.add_argument("--language", type=str, default="Polish", help="Language to use (default: 'Polish')")
    parser.add_argument("--device", type=str, default="cuda", help="Device to use (default: 'cuda')")

    args = parser.parse_args()

    process_audio_files(args.input_folder, args.output_folder, args.model, args.language, args.device)


if __name__ == "__main__":
    main()
