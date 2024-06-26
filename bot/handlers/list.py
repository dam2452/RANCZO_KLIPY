import logging
from aiogram import Router, Bot, types, Dispatcher
from aiogram.types import FSInputFile
from bot.handlers.search import last_search_quotes
from tabulate import tabulate
import tempfile
import os
from aiogram.filters import Command
logger = logging.getLogger(__name__)
router = Router()

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
        logger.error(f"Error in handle_list_request: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_list_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
