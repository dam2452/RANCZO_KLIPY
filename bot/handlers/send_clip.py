import logging
import os
import tempfile
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.database import DatabaseManager
from bot.utils.video_handler import VideoManager
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()
@router.message(Command(commands=['wyslij', 'send', 'wys']))
async def send_clip(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username

        content = message.text.split()
        if len(content) < 2:
            await message.answer("📄 Podaj nazwę klipu. Przykład: /wyslij nazwa_klipu")
            logger.info("No clip name provided by user.")
            return

        clip_name = content[1]
        logger.info(f"User '{username}' requested to send clip: '{clip_name}'")

        clip = await DatabaseManager.get_clip_by_name(username, clip_name)
        if not clip:
            await message.answer(f"❌ Nie znaleziono klipu o nazwie '{clip_name}'.❌")
            logger.info(f"Clip '{clip_name}' not found for user '{username}'.")
            return

        video_data, start_time, end_time = clip
        if not video_data:
            await message.answer("⚠️ Plik klipu jest pusty.⚠️")
            logger.warning(f"Clip file is empty for clip '{clip_name}' by user '{username}'.")
            return

        temp_file_path = os.path.join(tempfile.gettempdir(), f"{clip_name}.mp4")

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(video_data)

        if os.path.getsize(temp_file_path) == 0:
            await message.answer("⚠️ Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.⚠️")
            logger.error(f"File is empty after writing clip '{clip_name}' for user '{username}'.")
            os.remove(temp_file_path)
            return

        video_manager = VideoManager(bot)
        await video_manager.send_video(message.chat.id, temp_file_path)

        os.remove(temp_file_path)  # Clean up the temporary file
        logger.info(f"Clip '{clip_name}' sent to user '{username}' and temporary file removed.")

    except Exception as e:
        logger.error(f"An error occurred while sending clip '{clip_name}' for user '{username}': {str(e)}")
        await message.answer("⚠️ Wystąpił błąd podczas wysyłania klipu.⚠️")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Clean up the temporary file

def register_send_clip_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
