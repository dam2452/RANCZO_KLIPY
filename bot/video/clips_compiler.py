import asyncio
import logging
from pathlib import Path
import subprocess
import tempfile
from typing import (
    Dict,
    List,
    Union,
)

from aiogram import Bot
from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import ClipType
from bot.settings import settings
from bot.utils.log import log_system_message
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import (
    FFMpegException,
    send_video,
)


class ClipsCompiler:
    @staticmethod
    async def __do_compile_clips(segment_files: List[Path], output_file: Path, logger: logging.Logger) -> None:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as concat_file:
            concat_file_path = Path(concat_file.name)

        try:
            with concat_file_path.open("w", encoding="utf-8") as f:
                for tmp_file in segment_files:
                    f.write(f"file '{tmp_file.as_posix()}'\n")

            command = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file_path),
                "-c", "copy", "-movflags", "+faststart", "-fflags", "+genpts",
                "-avoid_negative_ts", "1", str(output_file),
            ]

            process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr = await process.communicate()

            if process.returncode != 0:
                raise FFMpegException(f"FFmpeg error: {stderr.decode()}")

            await log_system_message(logging.INFO, f"Clips concatenated successfully into {output_file}", logger)
        except Exception as e:
            raise FFMpegException(f"Error during concatenation: {e}") from e
        finally:
            concat_file_path.unlink(missing_ok=True)

    @staticmethod
    async def __compile_clips(selected_clips: List[Dict[str, Union[Path, float]]], logger: logging.Logger) -> Path:
        #pylint: disable=too-many-try-statements
        temp_files = []
        try:
            for segment in selected_clips:
                start_time = segment["start"] - settings.EXTEND_BEFORE_COMPILE
                end_time = segment["end"] + settings.EXTEND_AFTER_COMPILE

                with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".mp4",
                ) as temp_file:
                    temp_file_path = Path(temp_file.name)
                    temp_files.append(temp_file_path)
                    await ClipsExtractor.extract_clip(
                        segment["video_path"], start_time, end_time, temp_file_path, logger,
                    )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as compiled_output:
                compiled_output_path = Path(compiled_output.name)

            await ClipsCompiler.__do_compile_clips(temp_files, compiled_output_path, logger)

            return compiled_output_path
        except Exception as e:
            raise FFMpegException(f"Error during clip compilation: {str(e)}") from e
        finally:
            for temp_file in temp_files:
                temp_file.unlink(missing_ok=True)

    @staticmethod
    async def __send_compiled_clip(message: Message, compiled_output: Path, bot: Bot, logger: logging.Logger) -> None:
        with compiled_output.open("rb") as f:
            compiled_clip_data = f.read()

        await DatabaseManager.insert_last_clip(
            chat_id=message.chat.id,
            segment={},
            compiled_clip=compiled_clip_data,
            clip_type=ClipType.COMPILED,
            adjusted_start_time=None,
            adjusted_end_time=None,
            is_adjusted=False,
        )

        await send_video(message, compiled_output, bot, logger)

    @staticmethod
    async def compile_and_send_clips(
            message: Message, selected_segments: List[Dict[str, Union[str, float]]], bot: Bot,
            logger: logging.Logger,
    ) -> Path:
        compiled_output = await ClipsCompiler.__compile_clips(selected_segments, logger)
        await ClipsCompiler.__send_compiled_clip(message, compiled_output, bot, logger)

        return compiled_output


async def process_compiled_clip(
        message: Message, compiled_output: Path, clip_type: ClipType,
) -> None:
    with compiled_output.open("rb") as f:
        compiled_clip_data = f.read()

    await DatabaseManager.insert_last_clip(
        chat_id=message.chat.id,
        segment={},
        compiled_clip=compiled_clip_data,
        clip_type=clip_type,
        adjusted_start_time=None,
        adjusted_end_time=None,
        is_adjusted=False,
    )
