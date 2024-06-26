import logging
from aiogram import Router, Bot, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from bot.search_transcriptions import find_segment_by_quote
from bot.utils.db import is_user_authorized
from tabulate import tabulate
import tempfile
import os

logger = logging.getLogger(__name__)
router = Router()

last_search_quotes = {}

@router.message(Command('szukaj'))
async def handle_search_request(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("Podaj cytat, który chcesz znaleźć.")
            return

        quote = ' '.join(content[1:])
        segments = await find_segment_by_quote(quote, return_all=True)

        if not segments:
            await message.answer("Nie znaleziono pasujących segmentów.")
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

        for i, (unique_key, segment) in enumerate(unique_segments.items(), start=1):
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

            if i == 5:
                break

        table = tabulate(
            segment_lines,
            headers=["#", "Odcinek", "Tytuł", "Czas"],
            tablefmt="pipe",
            colalign=("center", "center", "left", "right")
        )

        response += f"```\n{table}\n```"
        await message.answer(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in handle_search_request: {e}")
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

@router.message(Command('lista'))
async def handle_list_request(message: types.Message, bot: Bot):
    try:
        chat_id = message.chat.id

        if chat_id not in last_search_quotes:
            await message.answer("Nie znaleziono wcześniejszych wyników wyszukiwania.")
            return

        segments = last_search_quotes[chat_id]

        response = f"🔍 Znaleziono {len(segments)} pasujących segmentów:\n"
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

        table = tabulate(segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe", colalign=("left", "center", "left", "right"))
        response += f"{table}\n"

        temp_dir = tempfile.gettempdir()
        file_name = os.path.join(temp_dir, "Ranczo_Klipy_Results.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        input_file = FSInputFile(file_name)
        await bot.send_document(chat_id, input_file, caption="Znalezione segmenty")
        os.remove(file_name)
    except Exception as e:
        logger.error(f"Error in handle_list_request: {e}")
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_search_command(dispatcher):
    dispatcher.include_router(router)
