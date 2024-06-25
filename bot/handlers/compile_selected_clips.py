import logging
import ffmpeg
import tempfile
import os
from telebot import TeleBot
from io import BytesIO
from ..utils.db import get_clip_by_index, is_user_authorized, get_video_data_by_name
from ..video_processing import extract_clip, convert_seconds_to_time_str

logger = logging.getLogger(__name__)

def register_compile_selected_clips_handler(bot: TeleBot):
    @bot.message_handler(commands=['kompilujklipy'])
    def compile_selected_clips(message):
        try:
            if not is_user_authorized(message.from_user.username):
                bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
                return

            username = message.from_user.username
            content = message.text.strip().split()

            logger.debug(f"Message content: {content}")

            if len(content) < 2:
                bot.reply_to(message, "Podaj indeksy klipów do kompilacji w kolejności.")
                return

            selected_indices = []
            try:
                for index in content[1:]:
                    logger.debug(f"Processing index: {index}")
                    selected_indices.append(int(index))
            except ValueError as e:
                logger.error(f"ValueError: {e}")
                bot.reply_to(message, "Podano nieprawidłowy indeks. Użyj liczb całkowitych.")
                return

            logger.debug(f"Selected indices: {selected_indices}")

            temp_files = []
            concat_file_content = ""

            for index in selected_indices:
                logger.debug(f"Processing index: {index}")
                clip = get_clip_by_index(username, index)
                if not clip:
                    bot.reply_to(message, f"Nie znaleziono klipu o indeksie {index}.")
                    return

                clip_name, start_time, end_time, season, episode_number, is_compilation = clip
                if is_compilation:
                    bot.reply_to(message, f"Klip o indeksie {index} jest już kompilacją. Wybierz inne klipy.")
                    return

                logger.debug(f"Clip details: {clip}")

                # Odczyt danych binarnych z bazy danych i zapisanie ich jako plik wideo
                video_data = get_video_data_by_name(username, clip_name)
                logger.debug(f"Video data length: {len(video_data) if video_data else 'No data'}")
                if video_data is None:
                    bot.reply_to(message, f"Nie znaleziono danych wideo dla klipu '{clip_name}'.")
                    return

                video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                with open(video_path, 'wb') as f:
                    f.write(video_data)

                temp_files.append(video_path)

                # Extract clip using the method from video_processing.py
                temp_clip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                with open(temp_clip_file, 'wb') as output:
                    start_time_str = convert_seconds_to_time_str(start_time)
                    end_time_str = convert_seconds_to_time_str(end_time)
                    extract_clip(video_path, start_time_str, end_time_str, output)

                temp_files.append(temp_clip_file)

                # Add the segment to the concat file content
                concat_file_content += f"file '{temp_clip_file}'\n"

            logger.debug(f"Concat file content:\n{concat_file_content}")

            # Create a temporary concat file
            concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
            concat_file.write(concat_file_content)
            concat_file.close()

            logger.debug(f"Concat file created at: {concat_file.name}")

            # Create the output file
            compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            compiled_output.close()

            # Concatenate segments using the concat demuxer
            ffmpeg.input(concat_file.name, format='concat', safe=0).output(compiled_output.name, codec='copy').run(overwrite_output=True)

            # Read the output file to BytesIO
            with open(compiled_output.name, 'rb') as f:
                compiled_data = f.read()

            compiled_output_io = BytesIO(compiled_data)

            bot.send_video(message.chat.id, compiled_output_io, caption="Oto skompilowane klipy.")

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(concat_file.name)
            os.remove(compiled_output.name)

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}")
            bot.reply_to(message, "Wystąpił błąd podczas kompilacji klipów.")
