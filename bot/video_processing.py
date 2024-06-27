import subprocess
import asyncio
import logging
import ffmpeg

logger = logging.getLogger(__name__)

async def extract_clip(video_path, start_time, end_time, output_filename):
    duration = end_time - start_time

    command = [
        'ffmpeg',
        '-y',  # Add this option to force overwrite
        '-ss', str(start_time),
        '-i', video_path,
        '-t', str(duration),
        '-c', 'copy',
        '-movflags', '+faststart',
        '-fflags', '+genpts',
        '-avoid_negative_ts', '1',
        output_filename
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"FFmpeg error: {stderr.decode()}")
        raise Exception(f"❌ Błąd FFmpeg: {stderr.decode()}")
    logger.info(f"Clip extracted successfully: {output_filename}")

def convert_seconds_to_time_str(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_video_duration(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        logger.info(f"Video duration for '{file_path}': {duration} seconds")
        return duration
    except ffmpeg.Error as e:
        logger.error(f"Error getting video duration for '{file_path}': {e}")
        print(f"⚠️ Błąd podczas uzyskiwania długości wideo: {e}")
        return None
