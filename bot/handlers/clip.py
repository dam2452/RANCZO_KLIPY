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
            await message.answer("pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        quote = message.text[len('/klip '):].strip()
        if not quote:
            await message.answer("Please provide a quote after the '/klip' command.")
            return

        logger.info(f"Searching for quote: '{quote}'")
        segments = await find_segment_by_quote(quote, return_all=True)

        if segments:
            segment = segments[0]
            last_selected_segment[chat_id] = {'segment': segment, 'start_time': segment['start'],
                                              'end_time': segment['end']}
            logger.info(f"Found segment: {segment}")
            video_path = segment.get('video_path', 'Unknown')
            if video_path == 'Unknown':
                await message.answer("Video path not found for the selected segment.")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))

            if not os.path.exists(video_path):
                await message.answer("Video file does not exist.")
                return

            start_time_str = str(segment['start'])
            end_time_str = str(segment['end'])

            logger.info(f"Starting video extraction from {start_time_str} to {end_time_str} for video: {video_path}")
            await send_clip_to_telegram(bot, message.chat.id, video_path, start_time_str, end_time_str)
        else:
            logger.info(f"No segment found for quote: '{quote}'")
            await message.answer("No segment found for the given quote.")
    except Exception as e:
        logger.error(f"Error handling /klip command: {e}", exc_info=True)
        await message.answer("An error occurred while processing your request.")

def register_clip_command(dispatcher: Router):
    dispatcher.include_router(router)
