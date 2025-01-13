import argparse
import json
from pathlib import Path
import sys
from typing import Optional

import ffmpeg

from Preprocessing.ErrorLogger import ErrorLogger
from Preprocessing.utils import setup_logger


class AudioNormalizer:
    SUPPORTED_EXTENSIONS = [".mp4", ".mkv", ".avi"]

    def __init__(self, input_folder: str, output_folder: str):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.logger = setup_logger(self.__class__.__name__)
        self.error_logger = ErrorLogger(self.logger)

    def get_best_audio_stream(self, video_file: str) -> Optional[int]:
        try:
            probe = ffmpeg.probe(video_file, select_streams="a", show_streams=True)
            streams = probe.get("streams", [])
            if not streams:
                self.error_logger.log_error(f"No audio streams found in file: {video_file}")
                return None
            best_stream = max(streams, key=lambda s: int(s.get("bit_rate", 0)))
            return best_stream["index"]
        except (ffmpeg.Error, KeyError, json.JSONDecodeError) as e:
            self.error_logger.log_error(f"Error determining the best audio stream for file {video_file}: {e}")
            return None

    def convert_and_normalize_audio(self, video_file: str, audio_index: int, output_audio_file: str) -> None:
        try:
            temp_output_audio_file = output_audio_file.replace(".wav", "_temp.wav")
            ffmpeg.input(video_file, **{"map": f"0:{audio_index}"}) \
                .output(output_audio_file, acodec="pcm_s16le", ar=48000, ac=1) \
                .run(overwrite_output=True)
            self.logger.info(f"Converted audio: {output_audio_file}")

            ffmpeg.input(output_audio_file).output(temp_output_audio_file, af="dynaudnorm").run(overwrite_output=True)
            self.logger.info(f"Normalized audio: {temp_output_audio_file}")

            Path(temp_output_audio_file).replace(output_audio_file)
            self.logger.info(f"Replaced original file with normalized audio: {output_audio_file}")
        except ffmpeg.Error as e:
            self.error_logger.log_error(f"Error during audio conversion or normalization for file {video_file}: {e}")
        except OSError as e:
            self.error_logger.log_error(f"File operation error: {e}")

    def process_video_file(self, video_path: Path) -> None:
        audio_index = self.get_best_audio_stream(str(video_path))
        if audio_index is None:
            self.logger.warning(f"Skipping file due to missing audio streams: {video_path}")
            return

        relative_path = video_path.relative_to(self.input_folder)
        output_audio_file = self.output_folder / relative_path.with_suffix(".wav")
        output_audio_file.parent.mkdir(parents=True, exist_ok=True)

        self.convert_and_normalize_audio(str(video_path), audio_index, str(output_audio_file))

    def process_folder(self) -> None:
        if not self.input_folder.is_dir():
            self.error_logger.log_error(f"Invalid input folder: {self.input_folder}")
            raise ValueError(f"Invalid input folder: {self.input_folder}")

        for video_file in self.input_folder.rglob("*"):
            if video_file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.process_video_file(video_file)

    def run(self) -> int:
        self.logger.info("Starting audio normalization...")
        try:
            self.process_folder()
        except ValueError as e:
            self.logger.error(f"Critical error: {e}")
            return 2
        return self.error_logger.finalize()


def main() -> None:
    parser = argparse.ArgumentParser(description="Process video files by converting and normalizing audio to WAV.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder containing video files.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder for processed audio files.")

    args = parser.parse_args()

    normalizer = AudioNormalizer(input_folder=args.input_folder, output_folder=args.output_folder)
    exit_code = normalizer.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
