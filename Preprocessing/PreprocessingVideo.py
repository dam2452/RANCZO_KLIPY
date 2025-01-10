import argparse
import json
import logging
from pathlib import Path
import subprocess


def get_video_resolution(video_path: Path) -> tuple[int, int]:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(video_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])
        if not streams:
            raise ValueError(f"No video streams found in {video_path}")
        width = streams[0].get("width")
        height = streams[0].get("height")
        if width is None or height is None:
            raise ValueError(f"Could not parse width/height from {video_path}")
        return width, height
    except subprocess.CalledProcessError as e:
        logging.error(f"ffprobe error: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        raise


def convert_video(
        input_file: Path,
        output_file: Path,
        codec: str = "h264_nvenc",
        preset: str = "slow",
        crf: int = 31,
) -> None:
    width, height = get_video_resolution(input_file)

    if height < 1080:
        vf_filter = "yadif=0:-1:0"
    else:
        vf_filter = "yadif=0:-1:0,scale=-2:1080"

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-c:v", codec,
        "-preset", preset,
        "-profile:v", "main",
        "-cq:v", str(crf),
        "-c:a", "aac",
        "-b:a", "128k",
        "-ac", "2",
        "-vf", vf_filter,
        "-movflags", "+faststart",
        str(output_file),
    ]

    logging.info(f"Processing: {input_file} -> {output_file}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing {input_file}: {e}")


def convert_videos(
        input_dir: Path,
        output_dir: Path,
        codec: str = "h264_nvenc",
        preset: str = "slow",
        crf: int = 31,
) -> None:
    if not input_dir.is_dir():
        logging.error(f"Invalid input directory: {input_dir}")
        return

    for video_file in input_dir.rglob("*.mp4"):
        relative_path = video_file.relative_to(input_dir)
        output_path = output_dir / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        convert_video(video_file, output_path, codec, preset, crf)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Convert .mp4 videos to h264_nvenc with optional scaling to 1080p.")
    parser.add_argument("input_directory", type=str, help="Path to the input directory containing videos.")
    parser.add_argument("output_directory", type=str, help="Path to the output directory for converted videos.")
    parser.add_argument("--codec", type=str, default="h264_nvenc", help="Video codec (default: h264_nvenc).")
    parser.add_argument("--preset", type=str, default="slow", help="FFmpeg preset (default: slow).")
    parser.add_argument("--crf", type=int, default=31, help="Quality (default: 31, lower = better).")

    args = parser.parse_args()
    input_dir = Path(args.input_directory)
    output_dir = Path(args.output_directory)

    convert_videos(input_dir, output_dir, args.codec, args.preset, args.crf)


if __name__ == "__main__":
    main()
