import logging
import tempfile
import os
import asyncio
import subprocess
from io import BytesIO
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import is_user_authorized, save_clip
from bot.handlers.search import last_search_quotes
from bot.handlers.clip import last_selected_segment
from bot.video_processing import get_video_duration

logger = logging.getLogger(__name__)
router = Router()

async def concatenate_clips(segment_files, output_file):
    concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
    concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
    concat_file.write(concat_file_content)
    concat_file.close()

    command = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
        '-c', 'copy', '-movflags', '+faststart', '-fflags', '+genpts', '-avoid_negative_ts', '1', output_file
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    os.remove(concat_file.name)
    if process.returncode != 0:
        raise Exception(f"ffmpeg error: {stderr.decode()}")

@router.message(Command('kompiluj'))
async def compile_clips(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
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
            for idx, segment in enumerate(selected_segments):
                video_path = segment['video_path']
                start = max(0, segment['start'] - 5)  # Extend 5 seconds before
                end = segment['end'] + 5  # Extend 5 seconds after

                # Create a temporary segment file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                command = [
                    'ffmpeg', '-y',
                    '-ss', str(start),
                    '-i', video_path,
                    '-to', str(end - start),
                    '-c', 'copy',
                    '-movflags', '+faststart',
                    '-fflags', '+genpts',
                    '-avoid_negative_ts', '1',
                    temp_file.name
                ]

                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    raise Exception(f"ffmpeg error: {stderr.decode()}")

                temp_file.close()

            # Create the output file
            compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            compiled_output.close()

            # Concatenate segments using the concat demuxer
            await concatenate_clips(temp_files, compiled_output.name)

            file_size_mb = os.path.getsize(compiled_output.name) / (1024 * 1024)
            if file_size_mb > 50:
                await message.answer(
                    "❌ Skompilowany klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB. ❌")
                os.remove(compiled_output.name)
                return

            # Read the output file to BytesIO
            with open(compiled_output.name, 'rb') as f:
                compiled_data = f.read()

            compiled_output_io = BytesIO(compiled_data)

            # Store compiled clip info for saving
            last_selected_segment[chat_id] = {'compiled_clip': compiled_output_io, 'selected_segments': selected_segments}

            await bot.send_video(chat_id, FSInputFile(compiled_output.name))# caption="Oto skompilowane klipy.")

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(compiled_output.name)

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}", exc_info=True)
            await message.answer("Wystąpił błąd podczas kompilacji klipów.")

    except Exception as e:
        logger.error(f"Error handling /kompiluj command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_compile_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
