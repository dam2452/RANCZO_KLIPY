import logging
import os
import tempfile
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.search_transcriptions import find_segment_by_quote
from bot.utils.db import is_user_authorized
from bot.video_processing import extract_clip

logger = logging.getLogger(__name__)
router = Router()

# Definicja last_selected_segment
last_selected_segment = {}

@router.message(Command('klip'))
async def handle_clip_request(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
            logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
            return

        content = message.text.split()
        if len(content) < 2:
            await message.answer("🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?")
            logger.info("No quote provided by user.")
            return

        quote = ' '.join(content[1:])
        logger.info(f"User '{message.from_user.username}' is searching for quote: '{quote}'")
        segments = await find_segment_by_quote(quote, return_all=False)
        logger.info(f"Segments found for quote '{quote}': {segments}")

        if not segments:
            await message.answer("❌ Nie znaleziono pasujących segmentów.")
            logger.info(f"No segments found for quote: '{quote}'")
            return

        segment = segments[0] if isinstance(segments, list) else segments  # Handle dictionary response
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - 5)  # Extend 5 seconds before
        end_time = segment['end'] + 5  # Extend 5 seconds after

        logger.info(f"Processing segment: {segment}")
        output_filename = os.path.join(tempfile.gettempdir(), f"{segment['id']}_clip.mp4")
        logger.info(f"Output filename: {output_filename}")
        await extract_clip(video_path, start_time, end_time, output_filename)

        input_file = FSInputFile(output_filename)
        await bot.send_video(message.chat.id, input_file)
        os.remove(output_filename)
        logger.info(f"Clip for quote '{quote}' sent to user '{message.from_user.username}' and temporary file removed.")

        # Zapisz segment jako ostatnio wybrany
        last_selected_segment[message.chat.id] = segment
        logger.info(f"Segment saved as last selected for chat ID '{message.chat.id}'")

    except Exception as e:
        logger.error(f"Error handling /klip command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania Twojego żądania. Prosimy spróbować ponownie później.")
        logger.debug(f"Exception details: {e}")

def register_clip_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
