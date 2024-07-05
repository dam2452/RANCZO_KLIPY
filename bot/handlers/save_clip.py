import logging
import os
import tempfile
from aiogram import types, Router, Dispatcher, Bot
from aiogram.filters import Command
from bot.utils.database import DatabaseManager
from bot.handlers.handle_clip import last_selected_segment
from bot.handlers.compile_selected import last_compiled_clip
from bot.handlers.manual_clip import last_manual_clip
from bot.utils.video_handler import VideoManager, VideoProcessor
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.settings import EXTEND_BEFORE, EXTEND_AFTER

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command(commands=['zapisz', 'save', 'z']))
async def save_user_clip(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            await message.answer("📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu")
            logger.info("No clip name provided by user.")
            await DatabaseManager.log_system_message("INFO", "No clip name provided by user.")
            return

        clip_name = content[1]

        if not await DatabaseManager.is_clip_name_unique(chat_id, clip_name):
            await message.answer("⚠️ Klip o takiej nazwie już istnieje. Wybierz inną nazwę.⚠️")
            logger.info(f"Clip name '{clip_name}' already exists for user '{username}'.")
            await DatabaseManager.log_system_message("INFO", f"Clip name '{clip_name}' already exists for user '{username}'.")
            return

        if chat_id not in last_selected_segment and chat_id not in last_compiled_clip and chat_id not in last_manual_clip:
            await message.answer("⚠️ Najpierw wybierz segment za pomocą /klip, /wytnij lub skompiluj klipy.⚠️")
            logger.info("No segment selected, manual clip, or compiled clip available for user.")
            await DatabaseManager.log_system_message("INFO", "No segment selected, manual clip, or compiled clip available for user.")
            return

        segment_info = last_selected_segment.get(chat_id) or last_compiled_clip.get(chat_id) or last_manual_clip.get(chat_id)

        # Log relevant segment information, avoiding binary data
        if 'episode_info' in segment_info:
            logger.info(f"Segment Info: {segment_info['episode_info']}")
            await DatabaseManager.log_system_message("INFO", f"Segment Info: {segment_info['episode_info']}")
        else:
            logger.info("Segment Info: Compiled or manual clip without episode info")
            await DatabaseManager.log_system_message("INFO", "Segment Info: Compiled or manual clip without episode info")

        start_time = 0
        end_time = 0
        is_compilation = False
        season = None
        episode_number = None
        clip_path = None

        if 'compiled_clip' in segment_info:
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(output_filename, 'wb') as f:
                compiled_clip = segment_info['compiled_clip']
                if isinstance(compiled_clip, bytes):
                    f.write(compiled_clip)
                else:
                    f.write(compiled_clip.getvalue())
            is_compilation = True
        elif 'expanded_clip' in segment_info:
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(output_filename, 'wb') as f:
                expanded_clip = segment_info['expanded_clip']
                if isinstance(expanded_clip, bytes):
                    f.write(expanded_clip)
                else:
                    f.write(expanded_clip.getvalue())
            start_time = segment_info.get('expanded_start', 0)
            end_time = segment_info.get('expanded_end', 0)
            season = segment_info.get('episode_info', {}).get('season')
            episode_number = segment_info.get('episode_info', {}).get('episode_number')
        else:
            segment = segment_info
            clip_path = segment['video_path']
            start_time = segment['start']# - EXTEND_BEFORE
            end_time = segment['end']# + EXTEND_AFTER
            is_compilation = False
            season = segment['episode_info']['season']
            episode_number = segment['episode_info']['episode_number']

            video_manager = VideoManager(bot)
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)

        actual_duration = await VideoProcessor.get_video_duration(output_filename)
        if actual_duration is None:
            await message.answer("❌ Nie udało się zweryfikować długości klipu.❌")
            logger.error(f"Failed to verify the length of the clip '{clip_name}' for user '{username}'.")
            await DatabaseManager.log_system_message("ERROR", f"Failed to verify the length of the clip '{clip_name}' for user '{username}'.")
            os.remove(output_filename)
            return

        end_time = start_time + int(actual_duration)

        with open(output_filename, 'rb') as file:
            video_data = file.read()

        os.remove(output_filename)

        await DatabaseManager.save_clip(
            chat_id=chat_id,
            username=username,
            clip_name=clip_name,
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
            is_compilation=is_compilation,
            season=season,
            episode_number=episode_number
        )

        await message.answer(f"✅ Klip '{clip_name}' został zapisany pomyślnie. ✅")
        logger.info(f"Clip '{clip_name}' saved successfully for user '{username}'.")
        await DatabaseManager.log_system_message("INFO", f"Clip '{clip_name}' saved successfully for user '{username}'.")

    except Exception as e:
        logger.error(f"Error handling /zapisz command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error handling /zapisz command for user '{message.from_user.username}': {e}")

def register_save_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
