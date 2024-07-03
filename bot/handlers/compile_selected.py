import logging
import tempfile
import os
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from bot.utils.database import DatabaseManager
from bot.utils.video_handler import VideoManager
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command(commands=['polaczklipy', 'concatclips','pk']))
async def compile_selected_clips(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        if not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
            logger.warning(f"Unauthorized access attempt by user: {username}")
            return

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            await message.answer("📄 Podaj nazwy klipów do skompilowania w odpowiedniej kolejności.")
            logger.info("No clip names provided by user.")
            return

        clip_names = content[1:]

        selected_clips = []
        for clip_name in clip_names:
            clip = await DatabaseManager.get_clip_by_name(username, clip_name)
            if not clip:
                await message.answer(f"❌ Nie znaleziono klipu o nazwie '{clip_name}'.")
                logger.info(f"Clip '{clip_name}' not found for user '{username}'.")
                return
            selected_clips.append(clip)

        if not selected_clips:
            await message.answer("❌ Nie znaleziono pasujących klipów do kompilacji.")
            logger.info("No matching clips found for compilation.")
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

            # Create an instance of VideoManager
            video_manager = VideoManager(bot)

            # Concatenate segments using the concat demuxer
            await video_manager.concatenate_clips(temp_files, compiled_output.name)

            file_size_mb = os.path.getsize(compiled_output.name) / (1024 * 1024)
            if file_size_mb > 50:
                await message.answer(
                    "❌ Skompilowany klip jest za duży, aby go wysłać przez Telegram. Maksymalny rozmiar pliku to 50 MB. ❌")
                logger.warning(f"Compiled clip exceeds size limit: {file_size_mb:.2f} MB")
                os.remove(compiled_output.name)
                return

            # Send the compiled video
            await bot.send_video(chat_id, FSInputFile(compiled_output.name), supports_streaming=True, width=1920, height=1080)

            # Clean up temporary files
            for temp_file in temp_files:
                os.remove(temp_file)
            os.remove(compiled_output.name)
            logger.info(f"Compiled clip sent to user '{username}' and temporary files removed.")

        except Exception as e:
            logger.error(f"An error occurred while compiling clips: {e}", exc_info=True)
            await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")

    except Exception as e:
        logger.error(f"Error handling /polaczklipy command for user '{username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania.⚠️")

def register_compile_selected_clips_command(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
