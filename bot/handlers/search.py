import tempfile
import os
import logging
from tabulate import tabulate
from telebot import TeleBot
from ..utils.db import is_user_authorized
from ..search_transcriptions import find_segment_by_quote

logger = logging.getLogger(__name__)

last_search_quotes = {}

def register_search_handlers(bot: TeleBot):
    @bot.message_handler(commands=['szukaj'])
    def search_quotes(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            bot.reply_to(message, "Podaj cytat, który chcesz znaleźć.")
            return

        quote = ' '.join(content[1:])
        season_filter = content[2] if len(content) > 2 else None
        episode_filter = content[3] if len(content) > 3 else None
        segments = find_segment_by_quote(quote, season_filter, episode_filter, return_all=True)

        if not segments:
            bot.reply_to(message, "Nie znaleziono pasujących segmentów.")
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

        response = f"🔍 *Znaleziono {len(unique_segments)} pasujących segmentów:*\n\n"
        segment_lines = []

        for i, (unique_key, segment) in enumerate(unique_segments.items(), start=1):
            if i > 5:
                break
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

        table = tabulate(segment_lines, tablefmt="pipe", colalign=("left", "center", "left", "right"))
        response += f"```\n{table}\n```"

        bot.reply_to(message, response, parse_mode='Markdown')

    @bot.message_handler(commands=['lista'])
    def list_all_quotes(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        if chat_id not in last_search_quotes:
            bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
            return

        segments = last_search_quotes[chat_id]

        if not segments:
            bot.reply_to(message, "Nie znaleziono pasujących segmentów.")
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
            line = [i, episode_formatted, episode_title, time_formatted]
            segment_lines.append(line)

        table = tabulate(segment_lines, headers=["#", "Odcinek", "Tytuł", "Czas"], tablefmt="pipe", colalign=("left", "center", "left", "right"))
        response += f"{table}\n"

        temp_dir = tempfile.gettempdir()
        file_name = os.path.join(temp_dir, "Ranczo_Klipy_Results.txt")
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response)

        try:
            with open(file_name, 'rb') as file:
                bot.send_document(chat_id, file, caption="Znalezione segmenty", visible_file_name="Ranczo_Klipy_Results.txt")
        finally:
            os.remove(file_name)
