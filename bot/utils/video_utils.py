import logging
from typing import Optional

from ffmpeg.asyncio import FFmpeg

from bot.utils.database import DatabaseManager
from bot.utils.log import log_system_message

logger = logging.getLogger(__name__)


class FFmpegException(Exception):
    def __init__(self, stderr: str) -> None:
        self.message = f"FFMpeg error: {stderr}"
        super().__init__(self.message)


class VideoProcessor:
    @staticmethod
    async def extract_clip(video_path: str, start_time: float, end_time: float, output_filename: str) -> None:
        duration = end_time - start_time
        await log_system_message(
            logging.INFO,
            f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}", logger,
        )

        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(video_path, ss=start_time)
            .output(
                output_filename,
                t=duration,
                c='copy',
                movflags='+faststart',
                fflags='+genpts',
                avoid_negative_ts='1',
            )
        )

        try:
            await ffmpeg.execute()
            success_message = f"Clip extracted successfully: {output_filename}"
            logger.info(success_message)
            await DatabaseManager.log_system_message("INFO", success_message)
        except FFmpegException as e:
            err_message = f"Error extracting clip: {e}"
            logger.error(err_message)
            await DatabaseManager.log_system_message("ERROR", err_message)
            raise e
        except Exception as e:
            err_message = f"Unexpected error: {e}"
            logger.error(err_message, exc_info=True)
            await DatabaseManager.log_system_message("ERROR", err_message)
            raise e

    @staticmethod
    def convert_seconds_to_time_str(seconds: int) -> Optional[str]:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def time_str_to_seconds(time_str: str) -> Optional[int]:
        h, m, s = [int(part) for part in time_str.split(':')]
        return h * 3600 + m * 60 + s

    @staticmethod
    async def get_video_duration(file_path: str) -> Optional[float]:

        try:
            probe = await FFmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            logger.info(f"Video duration for '{file_path}': {duration} seconds")
            await DatabaseManager.log_system_message("INFO", f"Video duration for '{file_path}': {duration} seconds")
            return duration
        except FFmpegException as e:
            error_message = f"Error getting video duration for '{file_path}': {e}"
            logger.error(error_message)
            await DatabaseManager.log_system_message("ERROR", error_message)
            return None
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            logger.error(error_message, exc_info=True)
            await DatabaseManager.log_system_message("ERROR", error_message)
            raise
