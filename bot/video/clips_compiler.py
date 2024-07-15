import logging
import os
import tempfile
from typing import List

from aiogram import Bot
from aiogram.types import Message
from ffmpeg.asyncio import FFmpeg

from bot.database.global_dicts import last_clip
from bot.utils.log import log_system_message
from bot.video.utils import (
    FFMpegException,
    send_video,
)


class ClipsCompiler:
    @staticmethod
    async def __do_compile_clips(segment_files: List[str], output_file: str, logger: logging.Logger) -> None:
        concat_file_content = "\n".join([f"file '{file}'" for file in segment_files])
        concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        concat_file.write(concat_file_content)
        concat_file.close()

        ffmpeg = FFmpeg().option("y").input(concat_file.name, format="concat", safe="0").output(
            output_file, c="copy", movflags="+faststart", fflags="+genpts", avoid_negative_ts="1",
        )

        try:
            await ffmpeg.execute()
            await log_system_message(logging.INFO, f"Clips concatenated successfully into {output_file}", logger)
        except Exception as e:
            raise FFMpegException(str(e)) from e
        finally:
            os.remove(concat_file.name)

    @staticmethod
    async def __compile_clips(selected_clips_data: List[bytes], logger: logging.Logger) -> str:
        temp_files = []
        for video_data in selected_clips_data:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_files.append(temp_file.name)
            with open(temp_file.name, 'wb') as f:
                f.write(video_data)

        compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        compiled_output.close()

        await ClipsCompiler.__do_compile_clips(temp_files, compiled_output.name, logger)

        return compiled_output.name

    @staticmethod
    async def __send_compiled_clip(message: Message, compiled_output: str, bot: Bot, logger: logging.Logger) -> None:
        with open(compiled_output, 'rb') as f:
            compiled_clip_data = f.read()

        last_clip[message.chat.id] = {
            'compiled_clip': compiled_clip_data,
            'type': 'compiled',
        }

        await send_video(message, compiled_output, bot, logger)

    @staticmethod
    async def __clean_up_temp_files(selected_clips_data: List[bytes]) -> None:
        for temp_file in selected_clips_data:
            os.remove(temp_file)

    @staticmethod
    async def compile_and_send_clips(message: Message, selected_segments: List[bytes], bot: Bot, logger: logging.Logger) -> str:
        compiled_output = await ClipsCompiler.__compile_clips(selected_segments, logger)
        await ClipsCompiler.__send_compiled_clip(message, compiled_output, bot, logger)

        if os.path.exists(compiled_output):
            os.remove(compiled_output)

        await ClipsCompiler.__clean_up_temp_files(selected_segments)
        return compiled_output
