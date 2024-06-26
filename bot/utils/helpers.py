from aiogram.types import FSInputFile
import os
import logging
import tempfile
from bot.video_processing import extract_clip

logger = logging.getLogger(__name__)

async def send_clip_to_telegram(bot, chat_id, video_path, start_time, end_time):
    try:
        output_filename = tempfile.mktemp(suffix='.mp4')
        await extract_clip(video_path, start_time, end_time, output_filename)

        file_size = os.path.getsize(output_filename) / (1024 * 1024)
        logger.info(f"Clip size: {file_size} MB")

        if file_size > 50:  # Telegram has a 50 MB limit for video files
            await bot.send_message(chat_id, "The extracted clip is too large to send via Telegram.")
        else:
            input_file = FSInputFile(output_filename)  # Ensure the path is correct
            await bot.send_video(chat_id, input_file)

        os.remove(output_filename)
    except Exception as e:
        logger.error(f"Failed to send video clip: {e}", exc_info=True)
        await bot.send_message(chat_id, f"Failed to send video clip: {str(e)}")
