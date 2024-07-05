import logging
import os
import tempfile

from aiogram import (
    Bot,
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command
from aiogram.types import FSInputFile
from tabulate import tabulate

from bot.handlers.clip_search import (
    last_search_quotes,
    last_search_terms,
)
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.utils.database import DatabaseManager

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=['lista', 'list', 'l']))
async def handle_list_request(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        chat_id = message.chat.id

        if not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
            logger.warning(f"Unauthorized access attempt by user: {username}")
            await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {username}")
            return

        if chat_id not in last_search_quotes or chat_id not in last_search_terms:
            await message.answer("🔍 Nie znaleziono wcześniejszych wyników wyszukiwania.")
            logger.info(f"No previous search results found for chat ID {chat_id}.")
            await DatabaseManager.log_system_message("INFO", f"No previous search results found for chat ID {chat_id}.")
            return

        segments = last_search_quotes[chat_id]
        search_term = last_search_terms[chat_id]

        response = f"🔍 Znaleziono {len(segments)} pasujących segmentów dla zapytania '{search_term}':\n"
        segment_lines = []

        for i, segment in enumerate(segments, start=1):
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
            line = [i, episode_formatted, episode_title, time_formatted]
            segment_lines.append(line)

        table = tabulate(
            segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe",
            colalign=("left", "center", "left", "right"),
        )
        response += f"{table}\n"

        temp_dir = tempfile.gettempdir()
        sanitized_search_term = "".join([c for c in search_term if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(" ", "_")
        file_name = os.path.join(temp_dir, f"Ranczo_Klipy_Wyniki_{sanitized_search_term}.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await bot.send_document(chat_id, input_file, caption="📄 Znalezione cytaty")
        os.remove(file_name)
        logger.info(f"List of search results for term '{search_term}' sent to user {username}.")
        await DatabaseManager.log_user_activity(username, f"/lista {search_term}")
        await DatabaseManager.log_system_message("INFO", f"List of search results for term '{search_term}' sent to user {username}.")

    except Exception as e:
        logger.error(f"Error in handle_list_request for user {username}: {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error in handle_list_request for user {username}: {e}")


def register_list_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
