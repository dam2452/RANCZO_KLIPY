import asyncio
import logging
from pathlib import Path
import tempfile

from aiogram import Bot
from aiogram.types import Message

from bot.utils.log import log_system_message
from bot.video.utils import (
    FFMpegException,
    get_video_duration,
    send_video,
)


class ClipsExtractor:
    @staticmethod
    async def extract_clip(
        video_path: Path,
        start_time: float,
        end_time: float,
        output_filename: Path,
        logger: logging.Logger,
    ) -> None:
        duration = end_time - start_time
        await log_system_message(
            logging.INFO,
            f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}",
            logger,
        )

        command = [
            "ffmpeg",
            "-y",  # overwrite output files
            "-ss", str(start_time),
            "-i", str(video_path),
            "-t", str(duration),
            "-c", "copy",
            "-movflags", "+faststart",
            "-fflags", "+genpts",
            "-avoid_negative_ts", "1",
            "-loglevel", "error",
            str(output_filename),
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise FFMpegException(stderr.decode())

        await log_system_message(
            logging.INFO,
            f"Clip extracted successfully: {output_filename}",
            logger,
        )

        clip_duration = await get_video_duration(output_filename)
        await log_system_message(
            logging.INFO,
            f"Clip duration: {clip_duration}",
            logger,
        )

    @staticmethod
    async def extract_and_send_clip(
        video_path: Path,
        message: Message,
        bot: Bot,
        logger: logging.Logger,
        start_time: float,
        end_time: float,
    ) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            output_filename = Path(temp_file.name)

        try:
            await ClipsExtractor.extract_clip(
                video_path,
                start_time,
                end_time,
                output_filename,
                logger,
            )
            await send_video(message, output_filename, bot, logger)
        finally:
            if output_filename.exists():
                output_filename.unlink()
            await log_system_message(
                logging.INFO,
                f"Temporary file '{output_filename}' removed after sending clip.",
                logger,
            )
