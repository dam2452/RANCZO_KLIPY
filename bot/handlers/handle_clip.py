import logging
from aiogram import Router, types, Bot, Dispatcher
from aiogram.filters import Command
from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_handler import VideoManager
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

EXTEND_BEFORE = 5
EXTEND_AFTER = 5

# Definicja last_selected_segment
last_selected_segment = {}

@router.message(Command('klip'))
async def handle_clip_request(message: types.Message, bot: Bot):
    try:
        content = message.text.split()
        if len(content) < 2:
            await message.answer("🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?")
            logger.info("No quote provided by user.")
            return

        quote = ' '.join(content[1:])
        logger.info(f"User '{message.from_user.username}' is searching for quote: '{quote}'")

        # Korzystanie z SearchTranscriptions
        search_transcriptions = SearchTranscriptions(router)
        segments = await search_transcriptions.find_segment_by_quote(quote, return_all=False)
        logger.info(f"Segments found for quote '{quote}': {segments}")

        if not segments:
            await message.answer("❌ Nie znaleziono pasujących cytatów.❌")
            logger.info(f"No segments found for quote: '{quote}'")
            return

        segment = segments[0] if isinstance(segments, list) else segments  # Handle dictionary response
        video_path = segment['video_path']
        start_time = max(0, segment['start'] - EXTEND_BEFORE)
        end_time = segment['end'] + EXTEND_AFTER

        video_manager = VideoManager(bot)
        await video_manager.extract_and_send_clip(message.chat.id, video_path, start_time, end_time)

        # Zapisz segment jako ostatnio wybrany
        last_selected_segment[message.chat.id] = segment
        logger.info(f"Segment saved as last selected for chat ID '{message.chat.id}'")
    except Exception as e:
        logger.error(f"An error occurred while handling clip request: {str(e)}")
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania Twojego żądania.⚠️")

def register_clip_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
