import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from bot.handlers.clip import last_selected_segment
from bot.utils.db import DatabaseManager
from bot.utils.video_manager import VideoManager
from bot.handlers.search import last_search_quotes
from bot.middlewares.authorization import AuthorizationMiddleware
from bot.middlewares.error_handler import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

EXTEND_BEFORE = 5
EXTEND_AFTER = 5

@router.message(Command('rozszerz'))
async def handle_expand_request(message: types.Message, bot: Bot):
    try:
        chat_id = message.chat.id
        content = message.text.split()

        if len(content) not in (3, 4):
            await message.answer("ℹ️ Podaj numer klipu (opcjonalnie), sekundy przed i sekundy po.")
            logger.info("Invalid number of arguments provided by user.")
            return

        if len(content) == 4:
            index = int(content[1]) - 1
            extra_before = float(content[2])
            extra_after = float(content[3])
            if chat_id not in last_search_quotes:
                await message.answer("🔍 Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
                logger.info("No previous search results found for user.")
                return
            segments = last_search_quotes[chat_id]
            segment = segments[index]
        else:
            if chat_id not in last_selected_segment:
                await message.answer("❌ Nie znaleziono żadnego wybranego segmentu. Użyj najpierw komendy /klip lub /wybierz.")
                logger.info("No previously selected segment found for user.")
                return
            segment = last_selected_segment[chat_id]
            extra_before = float(content[1])
            extra_after = float(content[2])

        start_time = max(0, segment.get('expanded_start', segment['start']) - extra_before)
        end_time = segment.get('expanded_end', segment['end']) + extra_after
        video_path = segment['video_path']

        video_manager = VideoManager(bot)
        await video_manager.extract_and_send_clip(chat_id, video_path, start_time, end_time)

        last_selected_segment[chat_id]['expanded_start'] = start_time
        last_selected_segment[chat_id]['expanded_end'] = end_time

        logger.info(f"Expanded clip sent to user '{message.from_user.username}' and temporary file removed.")

    except Exception as e:
        logger.error(f"Error handling /rozszerz command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")

def register_expand_command(router: Router):
    router.message.register(handle_expand_request, Command(commands=["rozszerz"]))

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
