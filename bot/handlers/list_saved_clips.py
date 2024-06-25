import logging
from telebot import TeleBot
from bot.utils.db import is_user_authorized, get_saved_clips
from tabulate import tabulate

logger = logging.getLogger(__name__)

def register_list_clips_handler(bot: TeleBot):
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
