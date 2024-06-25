import logging
import os
from telebot import TeleBot
from ..utils.db import is_user_authorized
from ..utils.helpers import send_clip_to_telegram
from .clip import last_selected_segment
from .search import last_search_quotes
logger = logging.getLogger(__name__)

def register_select_command(bot: TeleBot):
    @bot.message_handler(commands=['wybierz'])
    def select_quote(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            bot.reply_to(message, "Podaj numer segmentu, który chcesz wybrać.")
            return

        try:
            segment_number = int(content[1])
        except ValueError:
            bot.reply_to(message, "Numer segmentu musi być liczbą.")
            return

        segments = last_search_quotes.get(chat_id)
        if not segments or segment_number < 1 or segment_number > len(segments):
            bot.reply_to(message, "Nieprawidłowy numer segmentu.")
            return

        segment = segments[segment_number - 1]
        last_selected_segment[chat_id] = {'segment': segment, 'start_time': segment['start'], 'end_time': segment['end']}

        video_path = segment.get('video_path', 'Unknown')
        if video_path == 'Unknown':
            bot.reply_to(message, "Nie znaleziono ścieżki wideo dla wybranego segmentu.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))
        send_clip_to_telegram(bot, chat_id, video_path, segment['start'], segment['end'])
