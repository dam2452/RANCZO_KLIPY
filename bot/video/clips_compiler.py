import asyncio
import logging
import os
import subprocess
import tempfile
from typing import (
    Dict,
    List,
    Union,
)

from aiogram import Bot
from aiogram.types import Message
from ffmpeg.ffmpeg import FFmpeg

from bot.database.global_dicts import last_clip
from bot.utils.log import log_system_message
from bot.video.utils import (
    FFMpegException,
    send_video,
)


class ClipsCompiler:
    @staticmethod
    async def __extract_segment(segment: Dict[str, Union[str, float]], logger: logging.Logger) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, delete_on_close=False , suffix=".mp4")
        temp_file.close()  # Close the file to ensure it's written to disk properly
        duration = segment['end'] - segment['start']
        ffmpeg = FFmpeg().option("y").input(segment['video_path'], ss=segment['start']).output(
            temp_file.name,
            t=duration,
            c='copy',
            movflags='+faststart',
            fflags='+genpts',
            avoid_negative_ts='1',
        )
        try:
            arguments = ffmpeg.arguments
            await log_system_message(logging.DEBUG, f"FFmpeg arguments for extracting segment: {arguments}", logger)

            ffmpeg.execute()
            return temp_file.name
        except Exception as e:
            await log_system_message(logging.ERROR, f"Error extracting segment: {e}", logger)
            raise FFMpegException(str(e)) from e

    @staticmethod
    async def __do_compile_clips(segment_files: List[str], output_file: str, logger: logging.Logger) -> None:
        concat_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        try:
            with open(concat_file.name, 'w', encoding="utf-8") as f:
                for tmp_file in segment_files:
                    f.write(f"file '{tmp_file}'\n")

            command = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
                '-c', 'copy', '-movflags', '+faststart', '-fflags', '+genpts',
                '-avoid_negative_ts', '1', output_file,
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = await process.communicate()
            os.remove(concat_file.name)

            await log_system_message(logging.INFO, f"Clips concatenated successfully into {output_file}", logger)
        except Exception as e:
            await log_system_message(logging.ERROR, f"Error during concatenation: {e}", logger)
            raise FFMpegException(str(e)) from e
        finally:
            if os.path.exists(concat_file.name):
                os.remove(concat_file.name)
            for temp_file in segment_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    @staticmethod
    async def __compile_clips(selected_clips: List[Dict[str, Union[str, float]]], logger: logging.Logger) -> str:
        temp_files = []
        try:
            for segment in selected_clips:
                temp_file = await ClipsCompiler.__extract_segment(segment, logger)
                temp_files.append(temp_file)

            compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            compiled_output.close()

            await ClipsCompiler.__do_compile_clips(temp_files, compiled_output.name, logger)

            return compiled_output.name
        except Exception as e:
            await ClipsCompiler.__clean_up_temp_files(temp_files)
            error_message = f"Error during clip compilation: {str(e)}"
            await log_system_message(logging.ERROR, error_message, logger)
            raise FFMpegException(error_message) from e

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
    async def __clean_up_temp_files(temp_files: List[str]) -> None:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    @staticmethod
    async def compile_and_send_clips(
        message: Message, selected_segments: List[Dict[str, Union[str, float]]], bot: Bot,
        logger: logging.Logger,
    ) -> str:
        compiled_output = await ClipsCompiler.__compile_clips(selected_segments, logger)
        await ClipsCompiler.__send_compiled_clip(message, compiled_output, bot, logger)

        if os.path.exists(compiled_output):
            os.remove(compiled_output)

        await ClipsCompiler.__clean_up_temp_files([compiled_output])
        return compiled_output
