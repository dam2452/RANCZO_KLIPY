import logging
import os
from typing import Optional

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    Message,
)
from ffmpeg.asyncio import FFmpeg

from bot.settings import Settings
from bot.utils.log import log_system_message


class FFMpegException(Exception):
    def __init__(self, stderr: str) -> None:
        self.message = f"FFMpeg error: {stderr}"
        super().__init__(self.message)


async def get_video_duration(file_path: str, logger: logging.Logger) -> Optional[float]:
    try:
        probe = await FFmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        await log_system_message(logging.INFO, f"Video duration for '{file_path}': {duration} seconds", logger)
        return duration
    except FFMpegException as e:
        await log_system_message(logging.ERROR, f"Error getting video duration for '{file_path}': {e}", logger)
        return None
    except Exception as e:
        await log_system_message(logging.ERROR, f"Unexpected error: {e}", logger)
        raise


async def send_video(message: Message, file_path: str, bot: Bot, logger: logging.Logger) -> None:
    input_file = FSInputFile(file_path)
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    await log_system_message(logging.INFO, f"{file_path} Clip size: {file_size:.2f} MB", logger)

    if file_size > Settings.TELEGRAM_FILE_SIZE_LIMIT_MB:
        await log_system_message(
            logging.WARN,
            f"Clip size {file_size:.2f} MB exceeds the {Settings.TELEGRAM_FILE_SIZE_LIMIT_MB} MB limit.",
            logger,
        )
        await bot.send_message(
            message.chat.id,
            "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌",
        )
    else:
        await bot.send_video(message.chat.id, input_file, supports_streaming=True, width=1920, height=1080)
        await log_system_message(logging.INFO, f"Sent video file: {file_path}", logger)
