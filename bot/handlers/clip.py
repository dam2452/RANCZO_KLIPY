import logging
import os
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from bot.search_transcriptions import find_segment_by_quote
from bot.utils.db import is_user_authorized
from bot.utils.helpers import send_clip_to_telegram

logger = logging.getLogger(__name__)

last_selected_segment = {}
router = Router()

@router.message(Command('klip'))
async def handle_clip_request(message: Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        quote = message.text[len('/klip '):].strip()
        if not quote:
            await message.answer("Podaj cytat po komendzie '/klip'.")
            return

        logger.info(f"Searching for quote: '{quote}'")
        segments = await find_segment_by_quote(quote, return_all=True)

        if segments:
            segment = segments[0]
            last_selected_segment[chat_id] = {'segment': segment, 'start_time': segment['start'], 'end_time': segment['end']}
            logger.info(f"Found segment: {segment}")
            video_path = segment.get('video_path', 'Unknown')
            if video_path == 'Unknown':
                await message.answer("Ścieżka do wideo nie została znaleziona dla wybranego segmentu.")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))

            if not os.path.exists(video_path):
                await message.answer("Plik wideo nie istnieje.")
                return

            start_time = float(segment['start'])
            end_time = float(segment['end'])

            logger.info(f"Starting video extraction from {start_time} to {end_time} for video: {video_path}")
            await send_clip_to_telegram(bot, message.chat.id, video_path, start_time, end_time)
        else:
            logger.info(f"No segment found for quote: '{quote}'")
            await message.answer("Nie znaleziono segmentu dla podanego cytatu.")
    except Exception as e:
        logger.error(f"Error handling /klip command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania Twojego żądania.")

def register_clip_command(dispatcher: Router):
    dispatcher.include_router(router)
