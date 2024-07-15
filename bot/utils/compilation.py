import os
import tempfile
from typing import List

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    Message,
)

from bot.utils.global_dicts import last_clip
from bot.utils.video_manager import VideoManager


async def compile_clips(selected_clips_data: List[bytes]) -> str:
    temp_files = []
    for video_data in selected_clips_data:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_files.append(temp_file.name)
        with open(temp_file.name, 'wb') as f:
            f.write(video_data)

    compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    compiled_output.close()

    await VideoManager.concatenate_clips(temp_files, compiled_output.name)

    return compiled_output.name


async def send_compiled_clip(chat_id: int, compiled_output: str, bot: Bot) -> None:
    with open(compiled_output, 'rb') as f:
        compiled_clip_data = f.read()

    last_clip[chat_id] = {
        'compiled_clip': compiled_clip_data,
        'type': 'compiled',
    }

    await bot.send_video(chat_id, FSInputFile(compiled_output), supports_streaming=True, width=1920, height=1080)


async def clean_up_temp_files(selected_clips_data: List[bytes]) -> None:
    for temp_file in selected_clips_data:
        os.remove(temp_file)


async def compile_and_send_clips(message: Message, selected_segments: List[bytes], bot: Bot) -> str:
    compiled_output = await compile_clips(selected_segments)
    await send_compiled_clip(message.chat.id, compiled_output, bot)
    if os.path.exists(compiled_output):
        os.remove(compiled_output)
    await clean_up_temp_files(selected_segments)
    return compiled_output
