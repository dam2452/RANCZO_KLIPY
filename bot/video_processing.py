import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

import subprocess
import asyncio

async def extract_clip(video_path, start_time, end_time, output_filename):
    duration = end_time - start_time

    command = [
        'ffmpeg',
        '-y',  # Add this option to force overwrite
        '-i', video_path,
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-movflags', '+faststart',
        '-fflags', '+genpts',
        output_filename
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"ffmpeg error: {stderr.decode()}")

def convert_seconds_to_time_str(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


