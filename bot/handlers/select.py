import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from bot.utils.db import is_user_authorized
from bot.utils.video_manager import VideoManager
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
        start_time = max(0, segment['start'] - 5)  # Extend 5 seconds before
        end_time = segment['end'] + 5  # Extend 5 seconds after

        video_manager = VideoManager(bot)
        await video_manager.extract_and_send_clip(chat_id, video_path, start_time, end_time)

        # Zapisz segment jako ostatnio wybrany
        last_selected_segment[chat_id] = segment
        logger.info(f"Segment {segment['id']} selected by user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error in select_quote for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")

def register_select_command(router: Router):
    router.message.register(handle_select_request, Command(commands=["wybierz"]))
