import logging
import os
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from bot.utils.db import is_user_authorized
from bot.utils.helpers import send_clip_to_telegram
from bot.handlers.clip import last_selected_segment

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('rozszerz'))
async def handle_expand_request(message: Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        args = message.text[len('/rozszerz '):].strip().split()
        if len(args) != 2:
            await message.answer("Podaj czas rozszerzenia przed i po.")
            return

        if chat_id not in last_selected_segment:
            await message.answer("Brak ostatnio wybranego segmentu.")
            return

        start_time_adj = int(args[0])
        end_time_adj = int(args[1])

        segment = last_selected_segment[chat_id]['segment']
        start_time = float(segment['start']) - start_time_adj
        end_time = float(segment['end']) + end_time_adj

        video_path = segment.get('video_path', 'Unknown')
        if video_path == 'Unknown':
            await message.answer("Ścieżka do wideo nie została znaleziona dla wybranego segmentu.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))

        if not os.path.exists(video_path):
            await message.answer("Plik wideo nie istnieje.")
            return

        logger.info(f"Starting video extraction from {start_time} to {end_time} for video: {video_path}")
        await send_clip_to_telegram(bot, chat_id, video_path, start_time, end_time)
        await message.answer("Wysyłanie rozszerzonego klipu.")
    except Exception as e:
        logger.error(f"Error in handle_expand_request: {e}")
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_expand_command(dispatcher):
    dispatcher.include_router(router)
