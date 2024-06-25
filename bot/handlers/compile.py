import logging
import ffmpeg
import tempfile
import os
from telebot import TeleBot
from io import BytesIO
from ..utils.db import is_user_authorized
from .clip import last_selected_segment
from .search import last_search_quotes

logger = logging.getLogger(__name__)

def register_compile_command(bot: TeleBot):
    @bot.message_handler(commands=['kompiluj'])
    def compile_clips(message):
        if not is_user_authorized(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            bot.reply_to(message, "Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
            return

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            bot.reply_to(message, "Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
            return

        segments = last_search_quotes[chat_id]

        selected_segments = []
        for index in content[1:]:
            if index.lower() == "wszystko":
                selected_segments = segments
                break
            elif '-' in index:  # Check if it's a range
                try:
                    start, end = map(int, index.split('-'))
                    selected_segments.extend(segments[start - 1:end])  # Convert to 0-based index and include end
                except ValueError:
                    bot.reply_to(message, f"Podano nieprawidłowy zakres segmentów: {index}")
                    return
            else:
                try:
                    selected_segments.append(segments[int(index) - 1])  # Convert to 0-based index
                except (ValueError, IndexError):
                    bot.reply_to(message, f"Podano nieprawidłowy indeks segmentu: {index}")
                    return

        if not selected_segments:
            bot.reply_to(message, "Nie znaleziono pasujących segmentów do kompilacji.")
            return

        try:
            temp_files = []
            concat_file_content = ""

            for idx, segment in enumerate(selected_segments):
                video_path = segment['video_path']
                start = segment['start']
                end = segment['end']

                # Create a temporary segment file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                ffmpeg.input(video_path, ss=start, to=end).output(temp_file.name, codec='copy').run(overwrite_output=True)
                temp_file.close()

                # Add the segment to the concat file content
                concat_file_content += f"file '{temp_file.name}'\n"

            # Create a temporary concat file
            concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
            concat_file.write(concat_file_content)
            concat_file.close()

            # Create the output file
            compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            compiled_output.close()

            # Concatenate segments using the concat demuxer
            ffmpeg.input(concat_file.name, format='concat', safe=0).output(compiled_output.name, codec='copy').run(overwrite_output=True)

            # Read the output file to BytesIO
            with open(compiled_output.name, 'rb') as f:
                compiled_data = f.read()

            compiled_output_io = BytesIO(compiled_data)

            # Store compiled clip info for saving
            last_selected_segment[chat_id] = {'compiled_clip': compiled_output_io, 'selected_segments': selected_segments}

            bot.send_video(chat_id, compiled_output_io, caption="Oto skompilowane klipy.")

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(concat_file.name)
            os.remove(compiled_output.name)

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}")
            bot.reply_to(message, "Wystąpił błąd podczas kompilacji klipów.")
