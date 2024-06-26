import asyncio
import logging
import os

logger = logging.getLogger(__name__)

def convert_time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:  # MM:SS
        m, s = parts
        return int(m) * 60 + float(s)
    elif len(parts) == 1:  # SS.xxx
        return float(parts[0])
    else:
        raise ValueError(f"Invalid time format: {time_str}")

def convert_seconds_to_time_str(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02}.{milliseconds:03}"

async def extract_clip(video_path, start_time, end_time, output_filename):
    adjusted_start_time = max(start_time - 2, 0)
    adjusted_end_time = end_time + 2

    duration = adjusted_end_time - adjusted_start_time

    logger.info(f"Extracting clip from: {video_path}")
    logger.info(f"Start time (seconds): {start_time}, Adjusted start time: {adjusted_start_time}")
    logger.info(f"End time (seconds): {end_time}, Adjusted end time: {adjusted_end_time}")
    logger.info(f"Duration: {duration}")

    ffmpeg_command = [
        'ffmpeg',
        '-y',  # Add this option to force overwrite
        '-i', video_path,
        '-ss', str(adjusted_start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-movflags', '+faststart',
        '-fflags', '+genpts',
        output_filename
    ]

    logger.info(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")

    try:
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        logger.info("ffmpeg process started...")

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)  # 2 minutes timeout
            logger.info(f"ffmpeg process stdout: {stdout.decode()}")
            logger.info(f"ffmpeg process stderr: {stderr.decode()}")
        except asyncio.TimeoutError:
            process.kill()
            stdout, stderr = await process.communicate()
            logger.error(f"ffmpeg process timed out. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
            raise

        if process.returncode != 0:
            logger.error(f"ffmpeg process failed with return code {process.returncode}")
            raise RuntimeError(f"ffmpeg process failed with return code {process.returncode}")

        logger.info("ffmpeg process completed successfully.")

    except Exception as e:
        logger.error(f"Error during video extraction: {e}", exc_info=True)
        raise

def get_video_duration(input_file):
    """
    Returns the duration of the video in HH:MM:SS.xxx format.

    Parameters:
    - input_file: Path to the video file.
    """
    try:
        probe = ffmpeg.probe(input_file)
        duration = float(probe['format']['duration'])

        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration - int(duration)) * 1000)

        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
        return formatted_duration
    except ffmpeg.Error as e:
        logger.error(f"Error occurred during video duration retrieval: {e}")
        return "00:00:00.000"

def compress_to_target_size(input_file, output_file, target_size_mb=49):
    """
    Compresses a video file to a target size using the H.265 (libx265) codec, ensuring compatibility with specified devices.
    The video is standardized to 1080p resolution and deinterlaced if necessary. Audio stream is not modified.

    Parameters:
    - input_file: Path to the input video file.
    - output_file: Path where the output video will be saved.
    - target_size_mb: Target size of the output file in megabytes (MB).
    """
    formatted_duration = get_video_duration(input_file)
    if formatted_duration == "00:00:00.000":
        logger.error("Error: Unable to retrieve video duration or video is empty.")
        return False

    video_duration = convert_time_to_seconds(formatted_duration)

    # Calculate target total bitrate in kbps, taking into account the length of the video and desired target size.
    target_total_bitrate_kbps = (target_size_mb * 8 * 1024) / video_duration

    if target_total_bitrate_kbps < 1:
        logger.error("Error: Target size too small for given video.")
        return False

    # Use ffmpeg to compress the video without modifying the audio
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file,
                    vcodec='libx265', crf=28, preset='superfast',
                    vf='yadif=0:-1:0,scale=1920:1080',
                    video_bitrate=f'{int(target_total_bitrate_kbps)}k',
                    movflags='+faststart',
                    reset_timestamps=1,
                    loglevel='error',
                    map='0')
            .run(overwrite_output=True)
        )
        logger.info(f"Video compressed to {target_size_mb}MB and saved to {output_file}")
        return True
    except ffmpeg.Error as e:
        logger.error(f"Error occurred during video compression: {e}")
        return False
