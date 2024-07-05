import logging
from aiogram import Router, types, Bot, Dispatcher
from aiogram.filters import Command
from bot.utils.video_handler import VideoManager
from bot.utils.database import DatabaseManager
from bot.handlers.clip_search import last_search_quotes
from bot.handlers.handle_clip import last_selected_segment
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command(commands=['wybierz', 'select', 'w']))
async def handle_select_request(message: types.Message, bot: Bot):
    try:
        chat_id = message.chat.id
        username = message.from_user.username
        content = message.text.split()
        if len(content) < 2:
            await message.answer("📋 Podaj numer segmentu, który chcesz wybrać. Przykład: /wybierz 1")
            logger.info("No segment number provided by user.")
            await DatabaseManager.log_system_message("INFO", "No segment number provided by user.")
            return

        if chat_id not in last_search_quotes:
            await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
            logger.info("No previous search results found for user.")
            await DatabaseManager.log_system_message("INFO", "No previous search results found for user.")
            return

        index = int(content[1]) - 1
        segments = last_search_quotes[chat_id]

        if index < 0 or index >= len(segments):
            await message.answer("❌ Nieprawidłowy numer segmentu.❌")
            logger.warning(f"Invalid segment number provided by user: {index + 1}")
            await DatabaseManager.log_system_message("WARNING", f"Invalid segment number provided by user: {index + 1}")
            return

        segment = segments[index]
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - 5)  # Extend 5 seconds before
        end_time = segment['end'] + 5  # Extend 5 seconds after

        video_manager = VideoManager(bot)
        await video_manager.extract_and_send_clip(chat_id, video_path, start_time, end_time)

        # Zapisz segment jako ostatnio wybrany
        last_selected_segment[chat_id] = segment
        logger.info(f"Segment {segment['id']} selected by user '{username}'.")
        await DatabaseManager.log_user_activity(username, f"/wybierz {index + 1}")
        await DatabaseManager.log_system_message("INFO", f"Segment {segment['id']} selected by user '{username}'.")

    except Exception as e:
        logger.error(f"Error in select_quote for user '{username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error in select_quote for user '{username}': {e}")

def register_select_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
