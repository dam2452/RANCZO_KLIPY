import asyncio
import logging
import subprocess
from typing import Optional

import ffmpeg

from bot.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class VideoProcessor:
    @staticmethod
    async def extract_clip(video_path: str, start_time: int, end_time: int, output_filename: str) -> None:
        duration = end_time - start_time
        logger.info(f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}")
        await DatabaseManager.log_system_message(
            "INFO",
            f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}",
        )

        command = [
            'ffmpeg',
            '-y',  # Force overwrite
            '-ss', str(start_time),
            '-i', video_path,
            '-t', str(duration),
            '-c', 'copy',
            '-movflags', '+faststart',
            '-fflags', '+genpts',
            '-avoid_negative_ts', '1',
            output_filename,
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            error_message = f"❌ Błąd FFmpeg: {stderr.decode()}"
            logger.error(error_message)
            await DatabaseManager.log_system_message("ERROR", error_message)
            raise Exception(error_message)

        success_message = f"Clip extracted successfully: {output_filename}"
        logger.info(success_message)
        await DatabaseManager.log_system_message("INFO", success_message)

    @staticmethod
    def convert_seconds_to_time_str(seconds: int) -> Optional[str]:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def time_str_to_seconds(time_str: str) -> Optional[int]:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

    @staticmethod
    async def get_video_duration(file_path: str) -> Optional[float]:
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            logger.info(f"Video duration for '{file_path}': {duration} seconds")
            await DatabaseManager.log_system_message("INFO", f"Video duration for '{file_path}': {duration} seconds")
            return duration
        except ffmpeg.Error as e:
            error_message = f"Error getting video duration for '{file_path}': {e}"
            logger.error(error_message)
            await DatabaseManager.log_system_message("ERROR", error_message)
            return None
