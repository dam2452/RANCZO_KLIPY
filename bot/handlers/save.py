import logging
import io
from telebot import TeleBot
from bot.utils.db import is_user_authorized, save_clip, get_saved_clips, get_clip_by_name
from bot.handlers.clip import last_selected_segment
from tabulate import tabulate

logger = logging.getLogger(__name__)

def register_save_handlers(bot: TeleBot):
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

        if 'compiled_clip' in segment_info:
            clip_path = segment_info['compiled_clip']
            is_compilation = True
        else:
            segment = segment_info['segment']
            clip_path = segment['video_path']
            start_time = segment_info['start_time']
            end_time = segment_info['end_time']
            is_compilation = False


        try:
            with open(clip_path, 'rb') as f:
                if is_compilation:
                    video_data = f.read()
                    save_clip(message.from_user.username, clip_name, video_data, None, None, None, None, is_compilation)
                else:
                    f.seek(int(start_time))
                    video_data = f.read(int(end_time - start_time))
                    save_clip(message.from_user.username, clip_name, video_data, start_time, end_time,
                              segment.get('season', None), segment.get('episode', None), is_compilation)

            bot.reply_to(message, f"Klip '{clip_name}' został zapisany.")

        except Exception as e:
            logger.error(f"An error occurred while saving clip: {e}")
            bot.reply_to(message, "Wystąpił błąd podczas zapisywania klipu.")

    @bot.message_handler(commands=['mojeklipy'])
    def list_user_clips(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
            return

        clips = get_saved_clips(message.from_user.username)
        if not clips:
            bot.reply_to(message, "Nie masz zapisanych klipów.")
            return

        clip_list = []
        for i, (clip_name, start_time, end_time, season, episode_number, is_compilation) in enumerate(clips, start=1):
            if is_compilation:
                duration_formatted = 'Kompilacja'
            else:
                duration = end_time - start_time
                minutes, seconds = divmod(duration, 60)
                duration_formatted = f"{minutes}m{seconds}s" if minutes else f"{seconds}s"
            season_episode = f"S{str(season).zfill(2)}E{str(episode_number).zfill(2)}" if season and episode_number else "Kompilacja"
            clip_list.append([i, clip_name, season_episode, duration_formatted])

        response = tabulate(clip_list, headers=["#", "Nazwa Klipu", "Sezon/Odcinek", "Długość"], tablefmt="grid")

        # Add formatting for Telegram
        formatted_response = f"```\n{response}\n```"

        bot.reply_to(message, f"Twoje zapisane klipy:\n\n{formatted_response}", parse_mode='Markdown')

    @bot.message_handler(commands=['wyslijklip'])
    def send_saved_clip_command(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
            return

        content = message.text.split()
        if len(content) < 2:
            bot.reply_to(message, "Podaj nazwę klipu, który chcesz wysłać.")
            return

        name = content[1]

        try:
            clip = get_clip_by_name(message.from_user.username, name)
            if not clip:
                bot.reply_to(message, f"Nie znaleziono klipu o nazwie '{name}'.")
                return

            video_data, start_time, end_time = clip
            out_buf = io.BytesIO(video_data)
            out_buf.name = f"{name}.mp4"
            out_buf.seek(0)

            bot.send_video(message.chat.id, out_buf)
        except Exception as e:
            logger.error(f"An error occurred while sending clip: {e}")
            bot.reply_to(message, "Wystąpił błąd podczas wysyłania klipu.")
