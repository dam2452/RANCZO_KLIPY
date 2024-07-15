import logging
import os
import tempfile
from typing import List

from aiogram import Bot
from aiogram.types import FSInputFile
from ffmpeg.asyncio import FFmpeg

from bot.utils.log import log_system_message
from bot.utils.video_utils import VideoProcessor

logger = logging.getLogger(__name__)


class VideoManager:
    TELEGRAM_FILE_SIZE_LIMIT_MB: int = 50

    @staticmethod
    async def extract_and_send_clip(chat_id: int, video_path: str, start_time: float, end_time: float, bot: Bot) -> None:
        output_filename = tempfile.mktemp(suffix='.mp4')
        try:
            await VideoProcessor.extract_clip(video_path, start_time, end_time, output_filename)

            file_size = os.path.getsize(output_filename) / (1024 * 1024)
            await log_system_message(logging.INFO, f"{video_path} Clip size: {file_size:.2f} MB", logger)

            if file_size > VideoManager.TELEGRAM_FILE_SIZE_LIMIT_MB:
                await log_system_message(
                    logging.WARN,
                    f"Clip size {file_size:.2f} MB exceeds the {VideoManager.TELEGRAM_FILE_SIZE_LIMIT_MB} MB limit.",
                    logger,
                )
                await bot.send_message(
                    chat_id,
                    "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌",
                )
            else:
                input_file = FSInputFile(output_filename)
                await bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
                await log_system_message(logging.INFO, f"Sent video clip: {output_filename}", logger)
        finally:
            os.remove(output_filename)
            await log_system_message(logging.INFO, f"Temporary file '{output_filename}' removed after sending clip.", logger)

    @staticmethod
    async def send_video(chat_id: int, file_path: str, bot: Bot) -> None:
        input_file = FSInputFile(file_path)
        await bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
        await log_system_message(logging.INFO, f"Sent video file: {file_path}", logger)

    @staticmethod
    async def concatenate_clips(segment_files: List[str], output_file: str) -> None:
        concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
        concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        concat_file.write(concat_file_content)
        concat_file.close()

        ffmpeg = FFmpeg().option("y").input(concat_file.name, format="concat", safe="0").output(
            output_file, c="copy", movflags="+faststart", fflags="+genpts", avoid_negative_ts="1",
        )

        try:
            await ffmpeg.execute()
            await log_system_message(logging.INFO, f"Clips concatenated successfully into {output_file}", logger)
        finally:
            os.remove(concat_file.name)
