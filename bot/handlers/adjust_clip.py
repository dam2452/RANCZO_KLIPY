import logging
import os
import tempfile

from aiogram import (
    Bot,
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command

from bot.handlers.clip_search import last_search_quotes
from bot.handlers.handle_clip import last_selected_segment
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.settings import (
    EXTEND_AFTER,
    EXTEND_BEFORE,
)
from bot.utils.database import DatabaseManager
from bot.utils.video_handler import (
    VideoManager,
    VideoProcessor,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=['dostosuj', 'adjust', 'd']))
async def adjust_video_clip(message: types.Message, bot: Bot):
    try:
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) not in (3, 4):
            await message.answer(
                "📝 Podaj czas w formacie `<float> <float>` lub `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub /dostosuj 1 10.5 -15.2")
            logger.info("Invalid number of arguments provided by user.")
            await DatabaseManager.log_system_message("INFO", "Invalid number of arguments provided by user.")
            return

        if len(content) == 4:
            index = int(content[1]) - 1
            before_adjustment = float(content[2])
            after_adjustment = float(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                logger.info("No previous search results found for user.")
                await DatabaseManager.log_system_message("INFO", "No previous search results found for user.")
                return
            segments = last_search_quotes[chat_id]
            segment_info = segments[index]
        else:
            before_adjustment = float(content[1])
            after_adjustment = float(content[2])
            if chat_id not in last_selected_segment:
                await message.answer("⚠️ Najpierw wybierz cytat za pomocą /klip.⚠️")
                logger.info("No segment selected by user.")
                await DatabaseManager.log_system_message("INFO", "No segment selected by user.")
                return
            segment_info = last_selected_segment[chat_id]

        logger.info(f"Segment Info: {segment_info}")
        await DatabaseManager.log_system_message("INFO", f"Segment Info: {segment_info}")

        original_start_time = segment_info['start'] - EXTEND_BEFORE
        original_end_time = segment_info['end'] + EXTEND_AFTER

        start_time = original_start_time - before_adjustment
        end_time = original_end_time + after_adjustment

        if start_time < 0:
            start_time = 0
        if end_time <= start_time:
            await message.answer("⚠️ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.⚠️")
            logger.info("End time must be later than start time.")
            await DatabaseManager.log_system_message("INFO", "End time must be later than start time.")
            return

        clip_path = segment_info['video_path']
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        try:
            await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)
            file_size = os.path.getsize(output_filename) / (1024 * 1024)
            logger.info(f"Clip size: {file_size:.2f} MB")
            await DatabaseManager.log_system_message("INFO", f"Clip size: {file_size:.2f} MB")

            if file_size > 50:
                await message.answer(
                    "❌ Wyodrębniony klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB.❌",
                )
                logger.warning(f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
                await DatabaseManager.log_system_message("WARNING", f"Clip size {file_size:.2f} MB exceeds the 50 MB limit.")
            else:
                video_manager = VideoManager(bot)
                await video_manager.send_video(chat_id, output_filename)

            os.remove(output_filename)
            logger.info(f"Temporary file '{output_filename}' removed after sending clip.")
            await DatabaseManager.log_system_message("INFO", f"Temporary file '{output_filename}' removed after sending clip.")

            segment_info['start'] = start_time
            segment_info['end'] = end_time
            last_selected_segment[chat_id] = segment_info
            logger.info(f"Updated segment info for chat ID '{chat_id}'")
            await DatabaseManager.log_system_message("INFO", f"Updated segment info for chat ID '{chat_id}'")

        except Exception as e:
            logger.error(f"Failed to adjust video clip: {e}", exc_info=True)
            await message.answer(f"⚠️ Nie udało się zmienić klipu wideo: {str(e)}")
            await DatabaseManager.log_system_message("ERROR", f"Failed to adjust video clip: {e}")

        logger.info(f"Video clip adjusted successfully for user '{message.from_user.username}'.")
        await DatabaseManager.log_system_message("INFO", f"Video clip adjusted successfully for user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error in adjust_video_clip for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error in adjust_video_clip for user '{message.from_user.username}': {e}")


def register_adjust_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
