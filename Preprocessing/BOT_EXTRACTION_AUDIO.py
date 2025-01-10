import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import ffmpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_best_audio_stream(video_file: str) -> Optional[int]:
    try:
        probe = ffmpeg.probe(video_file, select_streams="a", show_streams=True)
        streams = probe.get("streams", [])
        if not streams:
            logger.warning(f"No audio streams found in file: {video_file}")
            return None
        best_stream = max(streams, key=lambda s: int(s.get("bit_rate", 0)))
        return best_stream["index"]
    except (ffmpeg.Error, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error determining the best audio stream for file {video_file}: {e}")
        return None


def convert_and_normalize_audio(video_file: str, audio_index: int, output_audio_file: str) -> None:
    try:
        temp_output_audio_file = output_audio_file.replace(".wav", "_temp.wav")
        ffmpeg.input(video_file, **{"map": f"0:{audio_index}"}) \
            .output(output_audio_file, acodec="pcm_s16le", ar=48000, ac=1) \
            .run(overwrite_output=True)
        logger.info(f"Converted audio: {output_audio_file}")

        ffmpeg.input(output_audio_file).output(temp_output_audio_file, af="dynaudnorm").run(overwrite_output=True)
        logger.info(f"Normalized audio: {temp_output_audio_file}")

        Path(temp_output_audio_file).replace(output_audio_file)
        logger.info(f"Replaced original file with normalized audio: {output_audio_file}")
    except ffmpeg.Error as e:
        logger.error(f"Error during audio conversion or normalization for file {video_file}: {e}")
    except OSError as e:
        logger.error(f"File operation error: {e}")


def process_video_file(video_path: Path, output_folder: Path) -> None:
    audio_index = get_best_audio_stream(str(video_path))
    if audio_index is None:
        logger.warning(f"Skipping file due to missing audio streams: {video_path}")
        return

    relative_path = video_path.relative_to(video_path.parent.parent)
    output_audio_file = output_folder / relative_path.with_suffix(".wav")
    output_audio_file.parent.mkdir(parents=True, exist_ok=True)

    convert_and_normalize_audio(str(video_path), audio_index, str(output_audio_file))


def process_folder(input_folder: str, output_folder: str) -> None:
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)

    if not input_folder.is_dir():
        logger.error(f"Invalid input folder: {input_folder}")
        return

    for video_file in input_folder.rglob("*"):
        if video_file.suffix.lower() in [".mp4", ".mkv", ".avi"]:
            process_video_file(video_file, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video files by converting and normalizing audio to WAV.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder containing video files.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder for processed audio files.")

    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder)
