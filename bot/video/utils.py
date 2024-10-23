import os
from pathlib import Path
import subprocess


class FFMpegException(Exception):
    def __init__(self, stderr: str) -> None:
        self.message = f"FFMpeg error: {stderr}"
        super().__init__(self.message)


async def get_video_duration(file_path: Path) -> float:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise FFMpegException(f"FFMpeg error with file {file_path}: {e.stderr}") from e

    try:
        duration = float(result.stdout.strip())
    except ValueError as e:
        raise ValueError(f"Could not convert duration to float for file {file_path}: {result.stdout}") from e

    return duration
