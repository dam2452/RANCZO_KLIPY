import asyncio
import logging
import subprocess
import ffmpeg

logger = logging.getLogger(__name__)

class VideoProcessor:
    @staticmethod
    async def extract_clip(video_path: str, start_time: int, end_time: int, output_filename: str):
        duration = end_time - start_time

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
            output_filename
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"FFmpeg error: {stderr.decode()}")
            raise Exception(f"❌ Błąd FFmpeg: {stderr.decode()}")
        logger.info(f"Clip extracted successfully: {output_filename}")

    @staticmethod
    def convert_seconds_to_time_str(seconds: int) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def time_str_to_seconds(time_str: str) -> int:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

    @staticmethod
    def get_video_duration(file_path: str) -> float:
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            logger.info(f"Video duration for '{file_path}': {duration} seconds")
            return duration
        except ffmpeg.Error as e:
            logger.error(f"Error getting video duration for '{file_path}': {e}")
            return None
