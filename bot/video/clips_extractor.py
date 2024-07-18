import logging
import os
import tempfile

from aiogram import Bot
from aiogram.types import Message
from ffmpeg.asyncio import FFmpeg

from bot.utils.log import log_system_message
from bot.video.utils import (
    FFMpegException,
    send_video,
)


class ClipsExtractor:
    @staticmethod
    async def extract_clip(video_path: str, start_time: float, end_time: float, output_filename: str, logger: logging.Logger) -> None:
        duration = end_time - start_time
        await log_system_message(
            logging.INFO,
            f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}", logger,
        )

        ffmpeg = FFmpeg().option("y").input(video_path, ss=start_time).output(
            output_filename,
            t=duration,
            c='copy',
            movflags='+faststart',
            fflags='+genpts',
            avoid_negative_ts='1',
        )

        try:
            await ffmpeg.execute()
            await log_system_message(logging.INFO, f"Clip extracted successfully: {output_filename}", logger)
        except Exception as e:
            await log_system_message(logging.ERROR, f"Error extracting clip: {e}", logger)
            raise FFMpegException(str(e)) from e

    @staticmethod
    async def extract_and_send_clip(
        video_path: str, message: Message, bot: Bot, logger: logging.Logger, start_time: float,
        end_time: float,
    ) -> None:
        output_filename = tempfile.mktemp(suffix='.mp4')
        try:
            await ClipsExtractor.extract_clip(video_path, start_time, end_time, output_filename, logger)
            await send_video(message, output_filename, bot, logger)
        finally:
            if os.path.exists(output_filename):
                os.remove(output_filename)
            await log_system_message(logging.INFO, f"Temporary file '{output_filename}' removed after sending clip.", logger)
