import logging
from telebot import TeleBot
from bot.utils.db import is_user_authorized, save_clip
from bot.handlers.clip import last_selected_segment
from ..video_processing import extract_clip, convert_seconds_to_time_str
import io

logger = logging.getLogger(__name__)

def register_save_clip_handler(bot: TeleBot):
    @bot.message_handler(commands=['zapisz'])
    def save_user_clip(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            bot.reply_to(message, "Podaj nazwę klipu.")
            return

        clip_name = content[1]

        if chat_id not in last_selected_segment:
            bot.reply_to(message, "Najpierw wybierz segment za pomocą /wybierz.")
            return

        segment_info = last_selected_segment[chat_id]
        logger.info(f"Segment Info: {segment_info}")

        if 'compiled_clip' in segment_info:
            video_data = segment_info['compiled_clip'].getvalue()
            is_compilation = True
            segment = segment_info['selected_segments'][0]
            episode_info = segment.get('episode_info')
            start_time = None
            end_time = None
        else:
            segment = segment_info['segment']
            clip_path = segment['video_path']
            start_time = segment_info['start_time']
            end_time = segment_info['end_time']
            is_compilation = False

            # Convert start and end times to HH:MM:SS.xxx format
            start_time_str = convert_seconds_to_time_str(start_time)
            end_time_str = convert_seconds_to_time_str(end_time)

            output = io.BytesIO()
            extract_clip(clip_path, start_time_str, end_time_str, output)
            video_data = output.getvalue()

            episode_info = segment.get('episode_info')

        logger.info(f"Episode Info: {episode_info}")
        if episode_info:
            season = episode_info.get('season')
            episode_number = episode_info.get('episode_number')
        else:
            season = None
            episode_number = None

        try:
            logger.info(f"Saving clip: {clip_name}, start_time: {start_time}, end_time: {end_time}, season: {season}, episode: {episode_number}, is_compilation: {is_compilation}")
            save_clip(message.from_user.username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation)

            bot.reply_to(message, f"Klip '{clip_name}' został zapisany.")
        except Exception as e:
            logger.error(f"Error saving clip: {str(e)}")
            bot.reply_to(message, f"Error saving clip: {str(e)}")
