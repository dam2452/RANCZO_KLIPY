import logging
from aiogram import types, Router
from aiogram.filters import Command
from bot.utils.db import is_user_authorized, save_clip
from bot.handlers.clip import last_selected_segment
from bot.video_processing import extract_clip, convert_seconds_to_time_str
import io

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command(commands=["zapisz"]))
async def save_user_clip(message: types.Message):
    if not await is_user_authorized(message.from_user.username):
        await message.answer("Nie masz uprawnień do korzystania z tego bota.")
        return

    chat_id = message.chat.id
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

    if 'compiled_clip' in segment_info:
        video_data = segment_info['compiled_clip'].getvalue()
        is_compilation = True
        selected_segments = segment_info['selected_segments']
        total_duration = sum(segment['end'] - segment['start'] for segment in selected_segments)
        start_time = 0  # Compiled clips do not have a single start time
        end_time = total_duration
        actual_duration = total_duration
        segment = selected_segments[0]
        episode_info = segment.get('episode_info')
    else:
        segment = segment_info['segment']
        clip_path = segment['video_path']
        start_time = segment_info['start_time']
        end_time = segment_info['end_time']
        is_compilation = False

        # Adjust start and end times for accurate extraction
        adjusted_start_time = max(0, start_time - 2)
        adjusted_end_time = end_time + 2

        # Extract the clip
        video_data = await extract_clip(clip_path, adjusted_start_time, adjusted_end_time)

    # Save the clip to the database
    await save_clip(
        chat_id=chat_id,
        clip_name=clip_name,
        video_data=video_data,
        start_time=start_time,
        end_time=end_time,
        is_compilation=is_compilation
    )

    await message.answer(f"Klip '{clip_name}' został zapisany pomyślnie.")

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
