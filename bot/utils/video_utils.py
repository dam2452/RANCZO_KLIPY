import logging
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile
from ffmpeg.asyncio import FFmpeg

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


async def send_video(chat_id: int, file_path: str, bot: Bot, logger: logging.Logger) -> None:
    input_file = FSInputFile(file_path)
    await bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
    await log_system_message(logging.INFO, f"Sent video file: {file_path}", logger)
