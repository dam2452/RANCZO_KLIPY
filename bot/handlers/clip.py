import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from bot.search_transcriptions import find_segment_by_quote
from bot.utils.video_manager import VideoManager  # Import VideoManager

logger = logging.getLogger(__name__)
router = Router()

# Definicja last_selected_segment
last_selected_segment = {}

@router.message(Command('klip'))
async def handle_clip_request(message: types.Message, bot: Bot):
    content = message.text.split()
    if len(content) < 2:
        await message.answer("🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?")
        logger.info("No quote provided by user.")
        return

    quote = ' '.join(content[1:])
    logger.info(f"User '{message.from_user.username}' is searching for quote: '{quote}'")
    segments = await find_segment_by_quote(quote, return_all=False)
    logger.info(f"Segments found for quote '{quote}': {segments}")

    if not segments:
        await message.answer("❌ Nie znaleziono pasujących cytatów.")
        logger.info(f"No segments found for quote: '{quote}'")
        return

    segment = segments[0] if isinstance(segments, list) else segments  # Handle dictionary response
    video_path = segment['video_path']
    start_time = max(0, segment['start'] - 5)  # Extend 5 seconds before
    end_time = segment['end'] + 5  # Extend 5 seconds after

    video_manager = VideoManager(bot)
    await video_manager.extract_and_send_clip(message.chat.id, video_path, start_time, end_time)

    # Zapisz segment jako ostatnio wybrany
    last_selected_segment[message.chat.id] = segment
    logger.info(f"Segment saved as last selected for chat ID '{message.chat.id}'")

def register_clip_command(router: Router):
    router.message.register(handle_clip_request, Command(commands=["klip"]))
