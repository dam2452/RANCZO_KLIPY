import json
import logging
from typing import (
    Dict,
    List,
)

from aiogram import (
    Bot,
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command

from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.utils.database import DatabaseManager
from bot.utils.transcription_search import SearchTranscriptions

logger = logging.getLogger(__name__)
router = Router()
dis = Dispatcher()

last_search_quotes: Dict[int, List[json]] = {}
last_search_terms: Dict[int, str] = {}


@router.message(Command(commands=['szukaj', 'search', 'sz']))
async def handle_search_request(message: types.Message, bot: Bot) -> None:
    try:
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("🔍 Podaj cytat, który chcesz znaleźć. Przykład: /szukaj geniusz")
            logger.info("No search quote provided by user.")
            await DatabaseManager.log_system_message("INFO", "No search quote provided by user.")
            return

        quote = ' '.join(content[1:])
        last_search_terms[chat_id] = quote
        logger.info(f"User '{message.from_user.username}' is searching for quote: '{quote}'")
        await DatabaseManager.log_user_activity(message.from_user.username, f"/szukaj {quote}")
        await DatabaseManager.log_system_message("INFO", f"User '{message.from_user.username}' is searching for quote: '{quote}'")

        search_transcriptions = SearchTranscriptions(dis)
        segments = await search_transcriptions.find_segment_by_quote(quote, return_all=True)
        logger.info(f"Segments found for quote '{quote}': {segments}")
        await DatabaseManager.log_system_message("INFO", f"Segments found for quote '{quote}': {segments}")

        if not segments:
            await message.answer("❌ Nie znaleziono pasujących cytatów.❌")
            logger.info(f"No segments found for quote: '{quote}'")
            await DatabaseManager.log_system_message("INFO", f"No segments found for quote: '{quote}'")
            return

        unique_segments = {}
        for segment in segments:
            episode_info = segment.get('episode_info', {})
            title = episode_info.get('title', 'Unknown')
            season = episode_info.get('season', 'Unknown')
            episode_number = episode_info.get('episode_number', 'Unknown')
            start_time = segment.get('start', 'Unknown')

            if season == 'Unknown' or episode_number == 'Unknown':
                continue

            unique_key = f"{title}-{season}-{episode_number}-{start_time}"
            if unique_key not in unique_segments:
                unique_segments[unique_key] = segment

        last_search_quotes[chat_id] = list(unique_segments.values())

        response = f"🔍 Znaleziono {len(unique_segments)} pasujących segmentów:\n"
        segment_lines = []

        for i, segment in enumerate(last_search_quotes[chat_id][:5], start=1):
            episode_info = segment.get('episode_info', {})
            total_episode_number = episode_info.get('episode_number', 'Unknown')
            season_number = (total_episode_number - 1) // 13 + 1 if isinstance(total_episode_number, int) else 'Unknown'
            episode_number_in_season = (total_episode_number - 1) % 13 + 1 if isinstance(
                total_episode_number,
                int,
            ) else 'Unknown'

            season = str(season_number).zfill(2)
            episode_number = str(episode_number_in_season).zfill(2)
            episode_title = episode_info.get('title', 'Unknown')
            start_time = int(segment['start'])
            minutes, seconds = divmod(start_time, 60)
            time_formatted = f"{minutes:02}:{seconds:02}"

            episode_formatted = f"S{season}E{episode_number}"
            line = f"{i}️⃣ | 📺{episode_formatted} | 🕒 {time_formatted} \n👉  {episode_title} "
            segment_lines.append(line)

        response += "```\n" + "\n\n".join(segment_lines) + "\n```"

        await message.answer(response, parse_mode='Markdown')
        logger.info(f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.")
        await DatabaseManager.log_system_message("INFO", f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error in handle_search_request for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error in handle_search_request for user '{message.from_user.username}': {e}")


def register_search_command(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)


router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
