import logging
from telebot import TeleBot
from bot.utils.db import get_clip_by_name
import os

logger = logging.getLogger(__name__)

def register_send_clip_handler(bot: TeleBot):
    @bot.message_handler(commands=['wyslijklip'])
    def send_clip(message):
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            bot.reply_to(message, "Podaj nazwę klipu.")
            return

        clip_name = content[1]
        username = message.from_user.username
        if not username:
            bot.reply_to(message, "Nie można zidentyfikować użytkownika.")
            return

        clip = get_clip_by_name(username, clip_name)
        if not clip:
            bot.reply_to(message, f"Nie znaleziono klipu o nazwie '{clip_name}'.")
            return

        video_data, start_time, end_time = clip
        if not video_data:
            bot.reply_to(message, "Plik klipu jest pusty.")
            return

        # Use current working directory for the temporary file
        temp_file_path = os.path.join(os.getcwd(), f"{clip_name}.mp4")

        try:
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(video_data)

            # Verify the file is not empty
            if os.path.getsize(temp_file_path) == 0:
                bot.reply_to(message, "Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.")
                os.remove(temp_file_path)
                return

            with open(temp_file_path, 'rb') as video:
                bot.send_video(chat_id, video, caption=f"Klip: {clip_name}")

            os.remove(temp_file_path)  # Clean up the temporary file
        except Exception as e:
            logger.error(f"An error occurred while sending clip: {str(e)}")
            bot.reply_to(message, "Wystąpił błąd podczas wysyłania klipu.")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)  # Clean up the temporary file
