import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from Preprocessing.ErrorHandlingLogger import ErrorHandlingLogger
from Preprocessing.utils import setup_logger
from bot.utils.functions import RESOLUTIONS


class VideoConverter:
    DEFAULT_CODEC: str = "h264_nvenc"
    DEFAULT_PRESET: str = "slow"
    DEFAULT_CRF: int = 31
    DEFAULT_GOP_SIZE: float = 0.5

    def __init__(self):
        self.logger: ErrorHandlingLogger = ErrorHandlingLogger(
            class_name=self.__class__.__name__,
            logger=setup_logger(self.__class__.__name__),
        )

    def run(self, args: argparse.Namespace) -> int:
        try:
            input_dir = Path(args.input_directory)
            output_dir = Path(args.output_directory)
            target_resolution = self.parse_resolution(args.resolution)

            self.logger.info("Starting video conversion...")
            self.convert_videos(input_dir, output_dir, target_resolution, args.codec, args.preset, args.crf, args.gop_size)
        except Exception as e: # pylint: disable=broad-exception-caught
            self.logger.error(f"Critical error during run: {e}")
        return self.logger.finalize()

    def convert_videos(
        self,
        input_dir: Path,
        output_dir: Path,
        target_resolution: Any,
        codec: str,
        preset: str,
        crf: int,
        gop_size: float,
    ) -> None:
        if not input_dir.is_dir():
            self.logger.error(f"Invalid input directory: {input_dir}")
            return

        for video_file in input_dir.rglob("*.mp4"):
            relative_path = video_file.relative_to(input_dir)
            output_path = output_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                self.convert_video(video_file, output_path, target_resolution, codec, preset, crf, gop_size)
            except Exception as e: # pylint: disable=broad-exception-caught
                self.logger.error(f"Error processing video {video_file}: {e}")

    def convert_video(
        self,
        input_file: Path,
        output_file: Path,
        target_resolution: Any,
        codec: str,
        preset: str,
        crf: int,
        gop_size: float,
    ) -> None:
        fps = self.get_video_properties(input_file)
        width, height = target_resolution
        vf_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
        )
        gop = int(fps * gop_size)

        command = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-c:v", codec,
            "-preset", preset,
            "-profile:v", "main",
            "-cq:v", str(crf),
            "-g", str(gop),
            "-c:a", "aac",
            "-b:a", "128k",
            "-ac", "2",
            "-vf", vf_filter,
            "-movflags", "+faststart",
            str(output_file),
        ]

        self.logger.info(f"Processing: {input_file} -> {output_file} with resolution {width}x{height}")
        subprocess.run(command, check=True)

    @staticmethod
    def get_video_properties(video_path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "json",
            str(video_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])
        if not streams:
            raise ValueError(f"No video streams found in {video_path}")

        r_frame_rate = streams[0].get("r_frame_rate")
        if not r_frame_rate:
            raise ValueError(f"Frame rate not found in {video_path}")

        num, denom = (int(x) for x in r_frame_rate.split('/'))
        return num / denom

    @staticmethod
    def parse_resolution(resolution: str) -> Any:
        if resolution not in RESOLUTIONS:
            raise ValueError(f"Invalid resolution {resolution}. Choose from: {list(RESOLUTIONS.keys())}")
        return RESOLUTIONS[resolution]


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert .mp4 videos to a specific resolution with black bars.")
    parser.add_argument("input_directory", type=Path, help="Path to the input directory containing videos.")
    parser.add_argument("output_directory", type=Path, help="Path to the output directory for converted videos.")
    parser.add_argument(
        "--resolution",
        type=str,
        default="1080p",
        choices=RESOLUTIONS.keys(),
        help="Target resolution for all videos.",
    )
    parser.add_argument("--codec", type=str, default=VideoConverter.DEFAULT_CODEC, help="Video codec.")
    parser.add_argument("--preset", type=str, default=VideoConverter.DEFAULT_PRESET, help="FFmpeg preset.")
    parser.add_argument("--crf", type=int, default=VideoConverter.DEFAULT_CRF, help="Quality (lower = better).")
    parser.add_argument("--gop-size", type=float, default=VideoConverter.DEFAULT_GOP_SIZE, help="Keyframe interval in seconds.")

    args = parser.parse_args()

    converter = VideoConverter()
    exit_code = converter.run(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
