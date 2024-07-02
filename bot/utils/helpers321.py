from aiogram.types import FSInputFile
import os
import logging
import tempfile
from bot.video_manager import extract_clip

logger = logging.getLogger(__name__)

async def send_clip_to_telegram(bot, chat_id, video_path, start_time, end_time):
    try:
        output_filename = tempfile.mktemp(suffix='.mp4')
        await extract_clip(video_path, start_time, end_time, output_filename)

        file_size = os.path.getsize(output_filename) / (1024 * 1024)
        logger.info(f"Clip size: {file_size:.2f} MB")

        if file_size > 50:  # Telegram has a 50 MB limit for video files
            await bot.send_message(chat_id, "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.")
            logger.warning(f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
        else:
            input_file = FSInputFile(output_filename)  # Ensure the path is correct
            await bot.send_video(chat_id, input_file, supports_streaming=True,width=1920, height=1080)# caption="🎥 Oto Twój klip! 🎥")

        os.remove(output_filename)
        logger.info(f"Temporary file '{output_filename}' removed after sending clip.")

    except Exception as e:
        logger.error(f"Failed to send video clip: {e}", exc_info=True)
        await bot.send_message(chat_id, f"⚠️ Nie udało się wysłać klipu wideo: {str(e)}")
