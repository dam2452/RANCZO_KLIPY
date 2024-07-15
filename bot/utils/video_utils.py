import logging
from typing import Optional

from ffmpeg.asyncio import FFmpeg

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
            await log_system_message(logging.INFO, f"Clip extracted successfully: {output_filename}", logger)
        except FFmpegException as e:
            await log_system_message(logging.ERROR, f"Error extracting clip: {e}", logger)
            raise e
        except Exception as e:
            await log_system_message(logging.ERROR, f"Unexpected error: {e}", logger)
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
            await log_system_message(logging.INFO, f"Video duration for '{file_path}': {duration} seconds", logger)
            return duration
        except FFmpegException as e:
            await log_system_message(logging.ERROR, f"Error getting video duration for '{file_path}': {e}", logger)
            return None
        except Exception as e:
            await log_system_message(logging.ERROR,f"Unexpected error: {e}", logger)
            raise
