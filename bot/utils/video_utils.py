import logging
from typing import Optional

import ffmpeg #fixme to jest jakieś gejowe bo jak dobrze pamiętam to musiałem instalować ffmpeg-python a używać ffmpeg żeby mi działało nwm XD

from bot.utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class FFmpegException(Exception):
    def __init__(self, stderr: str, return_code: int) -> None:
        self.message = f"FFMpeg error ({return_code}): {stderr}"
        super().__init__(self.message)


class VideoProcessor:
    @staticmethod
    async def extract_clip(video_path: str, start_time: float, end_time: float, output_filename: str) -> None:
        duration = end_time - start_time
        logger.info(f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}")
        await DatabaseManager.log_system_message(
            "INFO",
            f"Extracting clip from {video_path}, start: {start_time}, end: {end_time}, duration: {duration}",
        )

        try:
            ffmpeg.input(video_path, ss=start_time).output(
                output_filename,
                t=duration,
                c='copy',
                movflags='+faststart',
                fflags='+genpts',
                avoid_negative_ts='1'
            ).overwrite_output().run_async(pipe_stdout=True, pipe_stderr=True)

            success_message = f"Clip extracted successfully: {output_filename}"
            logger.info(success_message)
            await DatabaseManager.log_system_message("INFO", success_message)
        except ffmpeg.Error as e:
            err = FFmpegException(e.stderr.decode(), e.returncode) #fixme jakiś magic na potem
            logger.error(err.message)
            await DatabaseManager.log_system_message("ERROR", err.message)
            raise err

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
