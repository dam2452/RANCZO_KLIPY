import logging
import os
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.db import get_clip_by_name

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('wyslij'))
async def send_clip(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    content = message.text.split()
    if len(content) < 2:
        await message.answer("Podaj nazwę klipu.")
        return

    clip_name = content[1]
    username = message.from_user.username
    if not username:
        await message.answer("Nie można zidentyfikować użytkownika.")
        return

    clip = await get_clip_by_name(username, clip_name)
    if not clip:
        await message.answer(f"Nie znaleziono klipu o nazwie '{clip_name}'.")
        return

    video_data, start_time, end_time = clip
    if not video_data:
        await message.answer("Plik klipu jest pusty.")
        return

    # Use current working directory for the temporary file
    temp_file_path = os.path.join(os.getcwd(), f"{clip_name}.mp4")

    try:
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(video_data)

        # Verify the file is not empty
        if os.path.getsize(temp_file_path) == 0:
            await message.answer("Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.")
            os.remove(temp_file_path)
            return

        await bot.send_video(chat_id, FSInputFile(temp_file_path), caption=f"Klip: {clip_name}")

        os.remove(temp_file_path)  # Clean up the temporary file
    except Exception as e:
        logger.error(f"An error occurred while sending clip: {str(e)}")
        await message.answer("Wystąpił błąd podczas wysyłania klipu.")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Clean up the temporary file

def register_send_clip_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
