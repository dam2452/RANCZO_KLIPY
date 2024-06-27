import logging
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from bot.search_transcriptions import find_segment_by_quote
from bot.utils.db import is_user_authorized
from tabulate import tabulate

logger = logging.getLogger(__name__)
router = Router()

last_search_quotes = {}
last_search_terms = {}  # Add this dictionary to store search terms

@router.message(Command('szukaj'))
async def handle_search_request(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
            logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("🔍 Podaj cytat, który chcesz znaleźć. Przykład: /szukaj geniusz")
            logger.info("No search quote provided by user.")
            return

        quote = ' '.join(content[1:])
        last_search_terms[chat_id] = quote  # Store the search term
        logger.info(f"User '{message.from_user.username}' is searching for quote: '{quote}'")
        segments = await find_segment_by_quote(quote, return_all=True)
        logger.info(f"Segments found for quote '{quote}': {segments}")

        if not segments:
            await message.answer("❌ Nie znaleziono pasujących segmentów.")
            logger.info(f"No segments found for quote: '{quote}'")
            return

        unique_segments = {}
        for segment in segments:
            episode_info = segment.get('episode_info', {})
            title = episode_info.get('title', 'Unknown')
            season = episode_info.get('season', 'Unknown')
            episode_number = episode_info.get('episode_number', 'Unknown')
            start_time = segment.get('start', 'Unknown')

            if season == 'Unknown' or episode_number == 'Unknown':
                continue  # Skip segments with unknown season or episode number

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
            episode_number_in_season = (total_episode_number - 1) % 13 + 1 if isinstance(total_episode_number, int) else 'Unknown'

            season = str(season_number).zfill(2)
            episode_number = str(episode_number_in_season).zfill(2)
            episode_title = episode_info.get('title', 'Unknown')
            start_time = int(segment['start'])
            minutes, seconds = divmod(start_time, 60)
            time_formatted = f"{minutes:02}:{seconds:02}"

            episode_formatted = f"S{season}E{episode_number}"
            line = [f"{i}️⃣", episode_formatted, episode_title, time_formatted]
            segment_lines.append(line)

        table = tabulate(segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe", colalign=("left", "center", "left", "right"))
        response += f"```\n{table}\n```"

        await message.answer(response, parse_mode='Markdown')
        logger.info(f"Search results for quote '{quote}' sent to user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"Error in handle_search_request for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")

def register_search_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
