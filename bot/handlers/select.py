import logging
import os
from aiogram import Router, Bot, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from bot.utils.db import is_user_authorized
from bot.handlers.search import last_search_quotes

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('wybierz'))
async def select_quote(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("Podaj numer segmentu, który chcesz wybrać.")
            return

        try:
            segment_number = int(content[1])
        except ValueError:
            await message.answer("Numer segmentu musi być liczbą.")
            return

        segments = last_search_quotes.get(chat_id)
        if not segments or segment_number < 1 or segment_number > len(segments):
            await message.answer("Nieprawidłowy numer segmentu.")
            return

        segment = segments[segment_number - 1]

        video_path = segment.get('video_path', 'Unknown')
        if video_path == 'Unknown':
            await message.answer("Nie znaleziono ścieżki wideo dla wybranego segmentu.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))
        await bot.send_document(chat_id, FSInputFile(video_path))
    except Exception as e:
        logger.error(f"Error in select_quote: {e}")
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_select_command(dispatcher):
    dispatcher.include_router(router)
