import logging
import os
import tempfile
import ffmpeg
from telebot import TeleBot
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
            bot.reply_to(message,
                         "Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
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

        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"compiled_clips_{chat_id}.mp4")

        try:
            video_clips = []
            max_resolution = (0, 0)
            for segment in selected_segments:
                video_path = segment['video_path']
                start = segment['start']
                end = segment['end']
                video_clips.append((video_path, start, end))
                probe = ffmpeg.probe(video_path)
                video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
                if video_streams:
                    width = int(video_streams[0]['width'])
                    height = int(video_streams[0]['height'])
                    max_resolution = max(max_resolution, (width, height), key=lambda x: x[0] * x[1])

            concat_filter = ''
            for idx, (video_path, start, end) in enumerate(video_clips):
                input_file = ffmpeg.input(video_path, ss=start, t=(end - start))
                input_stream = input_file.video.filter('scale', max_resolution[0], max_resolution[1])
                audio_stream = input_file.audio
                temp_clip_path = os.path.join(temp_dir, f'clip{idx}.mp4')
                ffmpeg.output(input_stream, audio_stream, temp_clip_path).run()

            ffmpeg.concat(
                *[ffmpeg.input(os.path.join(temp_dir, f'clip{idx}.mp4')) for idx in range(len(video_clips))],
                v=1, a=1
            ).output(output_path).run()

            # Store compiled clip info for saving
            last_selected_segment[chat_id] = {'compiled_clip': output_path, 'selected_segments': selected_segments}

            with open(output_path, 'rb') as video:
                bot.send_video(chat_id, video, caption="Oto skompilowane klipy.")

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}")
            bot.reply_to(message, "Wystąpił błąd podczas kompilacji klipów.")

        finally:
            # Move cleanup to the save handler to avoid premature deletion
            last_selected_segment[chat_id]['temp_clip_paths'] = [os.path.join(temp_dir, f'clip{idx}.mp4') for idx in
                                                                 range(len(video_clips))]
