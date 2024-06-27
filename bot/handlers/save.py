import logging
import os
import tempfile
from aiogram import types, Router, Dispatcher
from aiogram.filters import Command
from bot.utils.db import is_user_authorized, save_clip
from bot.handlers.clip import last_selected_segment
from bot.video_processing import extract_clip, get_video_duration

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("zapisz"))
async def save_user_clip(message: types.Message):
    if not await is_user_authorized(message.from_user.username):
        await message.answer("Nie masz uprawnień do korzystania z tego bota.")
        return

    chat_id = message.chat.id
    username = message.from_user.username
    content = message.text.split()
    if len(content) < 2:
        await message.answer("Podaj nazwę klipu.")
        return

    clip_name = content[1]

    if chat_id not in last_selected_segment:
        await message.answer("Najpierw wybierz segment za pomocą /wybierz.")
        return

    segment_info = last_selected_segment[chat_id]
    logger.info(f"Segment Info: {segment_info}")

    video_data = None
    start_time = 0
    end_time = 0
    is_compilation = False
    season = None
    episode_number = None

    if 'compiled_clip' in segment_info:
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        with open(output_filename, 'wb') as f:
            f.write(segment_info['compiled_clip'].getvalue())
        is_compilation = True
    elif 'expanded_clip' in segment_info:
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        with open(output_filename, 'wb') as f:
            f.write(segment_info['expanded_clip'].getvalue())
        start_time = segment_info['start_time']
        end_time = segment_info['end_time']
        season = segment_info['season']
        episode_number = segment_info['episode_number']
    else:
        segment = segment_info
        clip_path = segment['video_path']
        start_time = max(0, segment['start'] - 5)  # Extend 5 seconds before
        end_time = segment['end'] + 5  # Extend 5 seconds after
        is_compilation = False
        season = segment['episode_info']['season']
        episode_number = segment['episode_info']['episode_number']

        # Extract the clip
        output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        await extract_clip(clip_path, start_time, end_time, output_filename)

    # Verify the video length using ffmpeg-python
    actual_duration = get_video_duration(output_filename)
    if actual_duration is None:
        await message.answer("❌ Nie udało się zweryfikować długości klipu.")
        os.remove(output_filename)
        return

    end_time = start_time + int(actual_duration)

    # Read the extracted clip data
    with open(output_filename, 'rb') as file:
        video_data = file.read()

    # Remove the temporary file
    os.remove(output_filename)

    # Save the clip to the database
    await save_clip(
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

    await message.answer(f"Klip '{clip_name}' został zapisany pomyślnie.")

def register_save_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
