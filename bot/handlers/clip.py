import logging
import os
from telebot import TeleBot
from ..search_transcriptions import find_segment_by_quote
from ..utils.db import is_user_authorized
from ..utils.helpers import send_clip_to_telegram

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
            # current_path = os.path.dirname(os.path.realpath(__file__))
            # print(current_path)
            # print(video_path)
            # print(base_dir)
            # send_clip_to_telegram(bot, message.chat.id, r"OLD/outputTEST28888.mp4", segment['start'], segment['end']) #tset
            # send_clip_to_telegram(bot, message.chat.id, r"C:\GIT_REPO\RANCZO_KLIPY\RANCZO-WIDEO\Sezon 7\Ranczo_S07E07.mp4", segment['start'], segment['end']) #tset
        else:
            logger.info(f"No segment found for quote: '{quote}'")
            bot.reply_to(message, "No segment found for the given quote.")
