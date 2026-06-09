import logging
import os
from pathlib import Path
import tempfile
from typing import (
    Dict,
    List,
)

from bot.utils.log import log_system_message
from bot.video.utils import run_ffmpeg_command

_CODEC_ARGS: Dict[str, List[str]] = {
    "mp3": ["-acodec", "libmp3lame", "-ab", "192k"],
    "wav": ["-acodec", "pcm_s16le"],
    "ogg": ["-acodec", "libvorbis", "-q:a", "4"],
    "flac": ["-acodec", "flac"],
}

SUPPORTED_AUDIO_FORMATS: List[str] = list(_CODEC_ARGS.keys())


class AudioExtractor:
    @staticmethod
    async def extract_audio(
        video_path: Path,
        audio_format: str,
        logger: logging.Logger,
    ) -> Path:
        if audio_format not in _CODEC_ARGS:
            raise ValueError(f"Unsupported audio format: {audio_format}. Supported: {SUPPORTED_AUDIO_FORMATS}")

        fd, tmp_path = tempfile.mkstemp(suffix=f".{audio_format}")
        os.close(fd)
        output_path = Path(tmp_path)

        await log_system_message(
            logging.INFO,
            f"Extracting audio from {video_path} as {audio_format}",
            logger,
        )

        command = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-vn",
            *_CODEC_ARGS[audio_format],
            "-loglevel", "error",
            str(output_path),
        ]

        await run_ffmpeg_command(command)

        await log_system_message(
            logging.INFO,
            f"Audio extracted successfully: {output_path}",
            logger,
        )

        return output_path
