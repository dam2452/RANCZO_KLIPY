import logging
import tempfile
import os
import ffmpeg
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import is_user_authorized, get_clip_by_name
from io import BytesIO

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('kompilujklipy'))
async def compile_selected_clips(message: types.Message, bot: Bot):
    try:
        if not await is_user_authorized(message.from_user.username):
            await message.answer("Nie masz uprawnień do korzystania z tego bota.")
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
            concat_file_content = ""

            for idx, clip in enumerate(selected_clips):
                video_data, start_time, end_time = clip

                # Create a temporary segment file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_files.append(temp_file.name)

                with open(temp_file.name, 'wb') as f:
                    f.write(video_data)

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
        logger.error(f"Error handling /kompilujklipy command: {e}", exc_info=True)
        await message.answer("Wystąpił błąd podczas przetwarzania żądania.")

def register_compile_selected_clips_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)
