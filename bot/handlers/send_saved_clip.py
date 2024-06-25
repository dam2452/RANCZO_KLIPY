import logging
import io
from telebot import TeleBot
from bot.utils.db import is_user_authorized, get_clip_by_name

logger = logging.getLogger(__name__)

def register_send_clip_handler(bot: TeleBot):
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
