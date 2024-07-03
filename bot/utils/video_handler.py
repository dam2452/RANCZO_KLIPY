import os
import logging
import tempfile
import asyncio
import subprocess
from aiogram import Bot
from aiogram.types import FSInputFile
from bot.utils.video_utils import VideoProcessor

logger = logging.getLogger(__name__)

class VideoManager:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def extract_and_send_clip(self, chat_id: int, video_path: str, start_time: int, end_time: int):
        try:
            output_filename = tempfile.mktemp(suffix='.mp4')
            await VideoProcessor.extract_clip(video_path, start_time, end_time, output_filename)

            file_size = os.path.getsize(output_filename) / (1024 * 1024)
            logger.info(f"Clip size: {file_size:.2f} MB")

            if file_size > 50:  # Telegram has a 50 MB limit for video files
                await self.bot.send_message(chat_id, "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌")
                logger.warning(f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
            else:
                input_file = FSInputFile(output_filename)
                await self.bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)

            os.remove(output_filename)
            logger.info(f"Temporary file '{output_filename}' removed after sending clip.")

        except Exception as e:
            logger.error(f"Failed to send video clip: {e}", exc_info=True)
            await self.bot.send_message(chat_id, f"⚠️ Nie udało się wysłać klipu wideo: {str(e)}")

    async def send_video(self, chat_id: int, file_path: str):
        try:
            input_file = FSInputFile(file_path)
            await self.bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
        except Exception as e:
            logger.error(f"Failed to send video clip: {e}", exc_info=True)
            await self.bot.send_message(chat_id, f"⚠️ Nie udało się wysłać klipu wideo: {str(e)}")

    async def extract_and_concatenate_clips(self, segments, output_filename):
        temp_files = []
        try:
            for segment in segments:
                video_path = segment['video_path']
                start = max(0, segment['start'] - 5)  # Extend 5 seconds before
                end = segment['end'] + 5  # Extend 5 seconds after

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                await VideoProcessor.extract_clip(video_path, start, end, temp_file.name)
                temp_file.close()

            await self.concatenate_clips(temp_files, output_filename)

        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    @staticmethod
    async def concatenate_clips(segment_files, output_file):
        concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
        concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        concat_file.write(concat_file_content)
        concat_file.close()

        command = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
            '-c', 'copy', '-movflags', '+faststart', '-fflags', '+genpts',
            '-avoid_negative_ts', '1', output_file
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        os.remove(concat_file.name)
        if process.returncode != 0:
            raise Exception(f"ffmpeg error: {stderr.decode()}")