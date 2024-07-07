import asyncio
import json
import logging
import os
import subprocess
import tempfile
from typing import List

from aiogram import Bot
from aiogram.types import FSInputFile

from bot.settings import Settings
from bot.utils.database import DatabaseManager
from bot.utils.video_utils import VideoProcessor

logger = logging.getLogger(__name__)


class VideoManager:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def extract_and_send_clip(self, chat_id: int, video_path: str, start_time: float, end_time: float) -> None:
        try:
            output_filename = tempfile.mktemp(suffix='.mp4')
            await VideoProcessor.extract_clip(video_path, start_time, end_time, output_filename)

            file_size = os.path.getsize(output_filename) / (1024 * 1024)
            logger.info(f"Clip size: {file_size:.2f} MB")
            await DatabaseManager.log_system_message("INFO", f"Clip size: {file_size:.2f} MB")

            if file_size > 50:  # Telegram has a 50 MB limit for video files
                await self.bot.send_message(
                    chat_id,
                    "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌",
                )
                logger.warning(f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
                await DatabaseManager.log_system_message("WARNING", f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
            else:
                input_file = FSInputFile(output_filename)
                await self.bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
                await DatabaseManager.log_system_message("INFO", f"Sent video clip: {output_filename}")
            os.remove(output_filename)
            logger.info(f"Temporary file '{output_filename}' removed after sending clip.")
            await DatabaseManager.log_system_message("INFO", f"Temporary file '{output_filename}' removed after sending clip.")

        except Exception as e:
            logger.error(f"Failed to send video clip: {e}", exc_info=True)
            await DatabaseManager.log_system_message("ERROR", f"Failed to send video clip: {e}")
            await self.bot.send_message(chat_id, f"⚠️ Nie udało się wysłać klipu wideo: {str(e)}")

    async def send_video(self, chat_id: int, file_path: str) -> None:
        try:
            input_file = FSInputFile(file_path)
            await self.bot.send_video(chat_id, input_file, supports_streaming=True, width=1920, height=1080)
            await DatabaseManager.log_system_message("INFO", f"Sent video file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to send video clip: {e}", exc_info=True)
            await DatabaseManager.log_system_message("ERROR", f"Failed to send video clip: {e}")
            await self.bot.send_message(chat_id, f"⚠️ Nie udało się wysłać klipu wideo: {str(e)}")

    async def extract_and_concatenate_clips(self, segments: List[json], output_filename: str) -> None:
        temp_files = []
        try:
            for segment in segments:
                video_path = segment['video_path']
                start = max(0, segment['start'] - Settings.EXTEND_BEFORE)
                end = segment['end'] + Settings.EXTEND_AFTER

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                await VideoProcessor.extract_clip(video_path, start, end, temp_file.name)
                temp_file.close()
                await DatabaseManager.log_system_message("INFO", f"Extracted clip from {video_path} ({start}-{end})")
            await self.concatenate_clips(temp_files, output_filename)
            await DatabaseManager.log_system_message("INFO", f"Concatenated clips into {output_filename}")
        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    await DatabaseManager.log_system_message("INFO", f"Temporary file '{temp_file}' removed after concatenation.")

    @staticmethod
    async def concatenate_clips(segment_files: List[str], output_file: str) -> None:
        concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
        concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        concat_file.write(concat_file_content)
        concat_file.close()

        command = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
            '-c', 'copy', '-movflags', '+faststart', '-fflags', '+genpts',
            '-avoid_negative_ts', '1', output_file,
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        os.remove(concat_file.name)

        if process.returncode != 0:
            logger.error(f"ffmpeg error: {stderr.decode()}")
            await DatabaseManager.log_system_message("ERROR", f"ffmpeg error: {stderr.decode()}")
            raise Exception(f"ffmpeg error: {stderr.decode()}")

        logger.info(f"Clips concatenated successfully into {output_file}")
        await DatabaseManager.log_system_message("INFO", f"Clips concatenated successfully into {output_file}")
