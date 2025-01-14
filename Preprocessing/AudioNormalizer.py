import argparse
from pathlib import Path
import sys
from typing import (
    List,
    Optional,
)

import ffmpeg

from Preprocessing.ErrorHandlingLogger import ErrorHandlingLogger
from Preprocessing.utils import setup_logger


class AudioNormalizer:
    SUPPORTED_EXTENSIONS: List[str] = [".mp4", ".mkv", ".avi"]

    def __init__(self, input_folder: str, output_folder: str):
        self.input_folder: Path = Path(input_folder)
        self.output_folder: Path = Path(output_folder)
        self.logger: ErrorHandlingLogger = ErrorHandlingLogger(
            class_name=self.__class__.__name__,
            logger=setup_logger(self.__class__.__name__),
        )

    def run(self) -> int:
        self.logger.info("Starting audio normalization...")
        try:
            self.process_folder()
        except Exception as e:
            self.logger.error(f"Unexpected critical error in run: {e}")
        return self.logger.finalize()

    def process_folder(self) -> None:
        try:
            if not self.input_folder.is_dir():
                self.logger.error(f"Invalid input folder: {self.input_folder}")
                raise ValueError(f"Invalid input folder: {self.input_folder}")

            for video_file in self.input_folder.rglob("*"):
                if video_file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    self.process_video_file(video_file)
        except Exception as e:
            self.logger.error(f"Unexpected error in process_folder: {e}")

    def process_video_file(self, video_path: Path) -> None:
        try:
            audio_index = self.get_best_audio_stream(str(video_path))
            if audio_index is None:
                self.logger.info(f"Skipping file due to missing audio streams: {video_path}")
                return

            relative_path = video_path.relative_to(self.input_folder)
            output_audio_file = self.output_folder / relative_path.with_suffix(".wav")
            output_audio_file.parent.mkdir(parents=True, exist_ok=True)

            self.convert_and_normalize_audio(str(video_path), audio_index, str(output_audio_file))
        except Exception as e:
            self.logger.error(f"Unexpected error in process_video_file for file {video_path}: {e}")

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
        except Exception as e:
            self.logger.error(f"Unexpected error in convert_and_normalize_audio for file {video_file}: {e}")

    def get_best_audio_stream(self, video_file: str) -> Optional[int]:
        try:
            probe = ffmpeg.probe(video_file, select_streams="a", show_streams=True)
            streams = probe.get("streams", [])
            if not streams:
                self.logger.error(f"No audio streams found in file: {video_file}")
                return None
            best_stream = max(streams, key=lambda s: int(s.get("bit_rate", 0)))
            return best_stream["index"]
        except Exception as e:
            self.logger.error(f"Unexpected error in get_best_audio_stream for file {video_file}: {e}")
            return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Process video files by converting and normalizing audio to WAV.")
    parser.add_argument("input_folder", type=Path, help="Path to the input folder containing video files.")
    parser.add_argument("output_folder", type=Path, help="Path to the output folder for processed audio files.")

    args = parser.parse_args()

    normalizer = AudioNormalizer(input_folder=args.input_folder, output_folder=args.output_folder)
    exit_code = normalizer.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
