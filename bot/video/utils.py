import logging
import os
import subprocess

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    Message,
)

from bot.settings import settings
from bot.utils.log import log_system_message


class FFMpegException(Exception):
    def __init__(self, stderr: str) -> None:
        self.message = f"FFMpeg error: {stderr}"
        super().__init__(self.message)


async def get_video_duration(file_path: str) -> float:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
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


async def send_video(message: Message, file_path: str, bot: Bot, logger: logging.Logger) -> None:
    input_file = FSInputFile(file_path)
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    await log_system_message(logging.INFO, f"{file_path} Clip size: {file_size:.2f} MB", logger)

    if file_size > settings.TELEGRAM_FILE_SIZE_LIMIT_MB:
        await log_system_message(
            logging.WARN,
            f"Clip size {file_size:.2f} MB exceeds the {settings.TELEGRAM_FILE_SIZE_LIMIT_MB} MB limit.",
            logger,
        )
        await bot.send_message(
            message.chat.id,
            "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌",
        )
    else:
        await bot.send_video(message.chat.id, input_file, supports_streaming=True, width=1920, height=1080)
        await log_system_message(logging.INFO, f"Sent video file: {file_path}", logger)
