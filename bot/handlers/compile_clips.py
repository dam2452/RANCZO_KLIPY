import logging
import tempfile
import os
from io import BytesIO
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.database import DatabaseManager
from bot.handlers.clip_search import last_search_quotes
from bot.handlers.handle_clip import last_selected_segment
from bot.utils.video_handler import VideoManager
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()
@router.message(Command(commands=['kompiluj', 'compile','kom']))
async def compile_clips(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    try:
        content = message.text.split()
        if len(content) < 2:
            await message.answer("🔄 Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
            logger.info("No segments provided by user.")
            return

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
            logger.info("No previous search results found for user.")
            return

        segments = last_search_quotes[chat_id]
        selected_segments = []

        for index in content[1:]:
            if index.lower() == "wszystko":
                selected_segments = segments
                break
            elif '-' in index:  # Check if it's a range
                try:
                    start, end = map(int, index.split('-'))
                    selected_segments.extend(segments[start - 1:end])  # Convert to 0-based index and include end
                except ValueError:
                    await message.answer(f"⚠️ Podano nieprawidłowy zakres segmentów: {index} ⚠️")
                    logger.warning(f"Invalid range provided by user: {index}")
                    return
            else:
                try:
                    selected_segments.append(segments[int(index) - 1])  # Convert to 0-based index
                except (ValueError, IndexError):
                    await message.answer(f"⚠️ Podano nieprawidłowy indeks segmentu: {index} ⚠️")
                    logger.warning(f"Invalid index provided by user: {index}")
                    return

        if not selected_segments:
            await message.answer("❌ Nie znaleziono pasujących segmentów do kompilacji.❌")
            logger.info("No matching segments found for compilation.")
            return

        video_manager = VideoManager(bot)
        compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        compiled_output.close()

        # Extract and concatenate segments
        await video_manager.extract_and_concatenate_clips(selected_segments, compiled_output.name)

        file_size_mb = os.path.getsize(compiled_output.name) / (1024 * 1024)
        if file_size_mb > 50:
            await message.answer("❌ Skompilowany klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB. ❌")
            logger.warning(f"Compiled clip exceeds size limit: {file_size_mb:.2f} MB")
            os.remove(compiled_output.name)
            return

        # Store compiled clip info for saving
        with open(compiled_output.name, 'rb') as f:
            compiled_data = f.read()

        compiled_output_io = BytesIO(compiled_data)
        last_selected_segment[chat_id] = {'compiled_clip': compiled_output_io, 'selected_segments': selected_segments}

        await bot.send_video(chat_id, FSInputFile(compiled_output.name), supports_streaming=True, width=1920, height=1080)
        os.remove(compiled_output.name)
        logger.info(f"Compiled clip sent to user '{message.from_user.username}' and temporary files removed.")

    except Exception as e:
        logger.error(f"An error occurred while compiling clips: {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")
        if 'compiled_output' in locals() and os.path.exists(compiled_output.name):
            os.remove(compiled_output.name)

def register_compile_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
