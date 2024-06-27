import logging
import os
import tempfile
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import is_user_authorized
from bot.video_processing import extract_clip
from bot.handlers.search import last_search_quotes
from bot.handlers.clip import last_selected_segment

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('wybierz'))
async def handle_select_request(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
            logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("📋 Podaj numer segmentu, który chcesz wybrać. Przykład: /wybierz 1")
            logger.info("No segment number provided by user.")
            return

        if chat_id not in last_search_quotes:
            await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
            logger.info("No previous search results found for user.")
            return

        index = int(content[1]) - 1
        segments = last_search_quotes[chat_id]

        if index < 0 or index >= len(segments):
            await message.answer("❌ Nieprawidłowy numer segmentu.")
            logger.warning(f"Invalid segment number provided by user: {index + 1}")
            return

        segment = segments[index]
        video_path = segment['video_path']
        start_time = segment['start']
        end_time = segment['end']

        output_filename = os.path.join(tempfile.gettempdir(), f"{segment['id']}_clip.mp4")
        await extract_clip(video_path, start_time, end_time, output_filename)

        input_file = FSInputFile(output_filename)
        await bot.send_video(message.chat.id, input_file, caption="🎥 Wybrany klip! 🎥")
        os.remove(output_filename)

        # Zapisz segment jako ostatnio wybrany
        last_selected_segment[chat_id] = segment
        logger.info(f"Segment {segment['id']} selected by user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error in select_quote for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")

def register_select_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
