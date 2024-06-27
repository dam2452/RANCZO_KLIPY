import logging
import tempfile
import os
import asyncio
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import is_user_authorized, get_clip_by_name

logger = logging.getLogger(__name__)
router = Router()

async def concatenate_clips(segment_files, output_file):
    concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
    concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
    concat_file.write(concat_file_content)
    concat_file.close()

    command = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
        '-c', 'copy', '-movflags', '+faststart', '-fflags', '+genpts',
        '-avoid_negative_ts', '1', output_file
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

@router.message(Command('polaczklipy'))
async def compile_selected_clips(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.")
            return

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            await message.answer("Podaj nazwy klipów do skompilowania w odpowiedniej kolejności.")
            return

        username = message.from_user.username
        clip_names = content[1:]

        selected_clips = []
        for clip_name in clip_names:
            clip = await get_clip_by_name(username, clip_name)
            if not clip:
                await message.answer(f"Nie znaleziono klipu o nazwie '{clip_name}'.")
                return
            selected_clips.append(clip)

        if not selected_clips:
            await message.answer("Nie znaleziono pasujących klipów do kompilacji.")
            return

        try:
            temp_files = []
            for clip in selected_clips:
                video_data, start_time, end_time = clip

                # Create a temporary segment file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                with open(temp_file.name, 'wb') as f:
                    f.write(video_data)

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

            # Send the compiled video
            await bot.send_video(chat_id, FSInputFile(compiled_output.name), caption="Oto skompilowane klipy.")

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(compiled_output.name)

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}", exc_info=True)
            await message.answer("Wystąpił błąd podczas kompilacji klipów.")

    except Exception as e:
        logger.error(f"Error handling /polaczklipy command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_compile_selected_clips_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
