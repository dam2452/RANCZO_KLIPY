import logging
import os
import io
from telebot import TeleBot
from ..search_transcriptions import find_segment_by_quote
from ..utils.db import is_user_authorized, is_user_moderator, is_user_admin
from ..utils.helpers import send_clip_to_telegram, extract_clip, convert_seconds_to_time_str
from .search import last_search_quotes

logger = logging.getLogger(__name__)

last_selected_segment = {}


def register_clip_handlers(bot: TeleBot):

    @bot.message_handler(commands=['klip'])
    def handle_clip_request(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        quote = message.text[len('/klip '):].strip()
        if not quote:
            bot.reply_to(message, "Please provide a quote after the '/klip' command.")
            return

        logger.info(f"Searching for quote: '{quote}'")
        segments = find_segment_by_quote(quote, return_all=True)

        if segments:
            segment = segments[0]
            last_selected_segment[chat_id] = segment
            logger.info(f"Found segment: {segment}")
            video_path = segment.get('video_path', 'Unknown')
            if video_path == 'Unknown':
                bot.reply_to(message, "Video path not found for the selected segment.")
                return
            base_dir = os.path.dirname(os.path.abspath(__file__))
            video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))
            send_clip_to_telegram(bot, message.chat.id, video_path, segment['start'], segment['end'])
        else:
            logger.info(f"No segment found for quote: '{quote}'")
            bot.reply_to(message, "No segment found for the given quote.")

    @bot.message_handler(commands=['rozszerz'])
    def expand_clip(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "pizgnął cię kto kiedy?")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 3 or (len(content) == 4 and not is_user_moderator(message.from_user.username) and not is_user_admin(message.from_user.username)):
            bot.reply_to(message, "Podaj numer segmentu oraz ilość sekund do dodania przed i po klipie.")
            return

        try:
            if len(content) == 3:
                segment = last_selected_segment.get(chat_id)
                if not segment:
                    bot.reply_to(message, "Najpierw użyj komendy '/klip' lub '/wybierz', aby znaleźć klip.")
                    return
                seconds_before = int(content[1])
                seconds_after = int(content[2])
                if not is_user_moderator(message.from_user.username) and not is_user_admin(message.from_user.username) and seconds_before + seconds_after > 20:
                    bot.reply_to(message, "Maksymalne rozszerzenie dla użytkowników na whitelist to 20 sekund łącznie.")
                    return
            else:
                segment_number = int(content[1])
                segments = last_search_quotes.get(chat_id)
                if not segments or segment_number < 1 or segment_number > len(segments):
                    bot.reply_to(message, "Nieprawidłowy numer segmentu.")
                    return
                segment = segments[segment_number - 1]
                last_selected_segment[chat_id] = segment
                seconds_before = int(content[2])
                seconds_after = int(content[3])
        except ValueError:
            bot.reply_to(message, "Numer segmentu i ilość sekund muszą być liczbami.")
            return

        start_time = max(segment['start'] - seconds_before, 0)
        end_time = segment['end'] + seconds_after
        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.normpath(os.path.join(base_dir, "..", "..", segment['video_path']))

        # Extract the clip to memory
        out_buf = io.BytesIO()
        out_buf.name = "clip.mp4"
        start_time_str = convert_seconds_to_time_str(start_time)
        end_time_str = convert_seconds_to_time_str(end_time)
        extract_clip(video_path, start_time_str, end_time_str, out_buf)

        # Check the size of the clip
        clip_size_mb = len(out_buf.getvalue()) / (1024 * 1024)
        if clip_size_mb > 50:
            bot.reply_to(message, "Rozszerzony klip przekracza 50MB i nie może zostać wysłany.")
            return

        # Send the clip
        out_buf.seek(0)
        bot.send_video(chat_id, out_buf)
        logger.info(f"Sent video clip from {start_time_str} to {end_time_str} to chat {chat_id}")

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
        last_selected_segment[chat_id] = segment

        video_path = segment.get('video_path', 'Unknown')
        if video_path == 'Unknown':
            bot.reply_to(message, "Nie znaleziono ścieżki wideo dla wybranego segmentu.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = os.path.normpath(os.path.join(base_dir, "..", "..", video_path))
        send_clip_to_telegram(bot, chat_id, video_path, segment['start'], segment['end'])
