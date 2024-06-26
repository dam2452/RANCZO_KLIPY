import logging
import tempfile
import os
import ffmpeg
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import is_user_authorized
from bot.handlers.clip import last_selected_segment
from bot.handlers.search import last_search_quotes

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('kompiluj'))
async def compile_clips(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            await message.answer("Proszę podać indeksy segmentów do skompilowania, zakres lub 'wszystko' do kompilacji wszystkich segmentów.")
            return

        if chat_id not in last_search_quotes or not last_search_quotes[chat_id]:
            await message.answer("Najpierw wykonaj wyszukiwanie za pomocą /szukaj.")
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
                    await message.answer(f"Podano nieprawidłowy zakres segmentów: {index}")
                    return
            else:
                try:
                    selected_segments.append(segments[int(index) - 1])  # Convert to 0-based index
                except (ValueError, IndexError):
                    await message.answer(f"Podano nieprawidłowy indeks segmentu: {index}")
                    return

        if not selected_segments:
            await message.answer("Nie znaleziono pasujących segmentów do kompilacji.")
            return

        try:
            temp_files = []
            concat_file_content = ""

            for idx, segment in enumerate(selected_segments):
                video_path = segment['video_path']
                start = max(0, segment['start'] - 5)  # Extend 5 seconds before
                end = segment['end'] + 5  # Extend 5 seconds after

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

            # Send the compiled video
            await bot.send_video(chat_id, FSInputFile(compiled_output.name), caption="Oto skompilowane klipy.")

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(concat_file.name)
            os.remove(compiled_output.name)

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}", exc_info=True)
            await message.answer("Wystąpił błąd podczas kompilacji klipów.")

    except Exception as e:
        logger.error(f"Error handling /kompiluj command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_compile_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
