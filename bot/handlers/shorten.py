import logging
import os
import tempfile
from aiogram import types, Router, Dispatcher, Bot
from aiogram.filters import Command
from bot.utils.db import is_user_authorized
from bot.utils.video_manager import VideoManager, VideoProcessor

logger = logging.getLogger(__name__)
router = Router()

last_selected_segment = {}

@router.message(Command("skroc"))
async def shorten_video_clip(message: types.Message, bot: Bot):
    if not await is_user_authorized(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    chat_id = message.chat.id
    content = message.text.split()
    if len(content) < 2:
        await message.answer("📝 Podaj czas zakończenia klipu. Przykład: /skroc 00:01:30")
        logger.info("No end time provided by user.")
        return

    end_time_str = content[1]

    if chat_id not in last_selected_segment:
        await message.answer("⚠️ Najpierw wybierz segment za pomocą /klip.")
        logger.info("No segment selected by user.")
        return

    segment_info = last_selected_segment[chat_id]
    logger.info(f"Segment Info: {segment_info}")

    video_data = None
    start_time = segment_info['start']
    end_time = VideoProcessor.time_str_to_seconds(end_time_str)
    clip_path = segment_info['video_path']

    if end_time <= start_time:
        await message.answer("⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.")
        logger.info("End time must be later than start time.")
        return

    output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    try:
        # Use VideoProcessor to trim the video
        await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)
        file_size = os.path.getsize(output_filename) / (1024 * 1024)
        logger.info(f"Clip size: {file_size:.2f} MB")

        if file_size > 50:  # Telegram has a 50 MB limit for video files
            await message.answer("❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.")
            logger.warning(f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
        else:
            # Send the trimmed video clip
            video_manager = VideoManager(bot)
            await video_manager.send_video(chat_id, output_filename)

        # Remove the temporary file
        os.remove(output_filename)
        logger.info(f"Temporary file '{output_filename}' removed after sending clip.")

    except Exception as e:
        logger.error(f"Failed to shorten video clip: {e}", exc_info=True)
        await message.answer(f"⚠️ Nie udało się skrócić klipu wideo: {str(e)}")

    await message.answer(f"✅ Klip został skrócony do {VideoProcessor.convert_seconds_to_time_str(end_time - start_time)}.")
    logger.info(f"Video clip shortened successfully for user '{message.from_user.username}'.")

def register_shorten_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
