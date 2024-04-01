import os
import time
import json
import subprocess
from cachetools.func import ttl_cache

# Constants
CACHE_DIR = os.path.join(os.getcwd(), "cache")

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

@ttl_cache(maxsize=100, ttl=3600)
def get_cached_clip_path(episode_path, start_time, end_time):
    clip_id = f"{os.path.basename(episode_path)}_{start_time}_{end_time}.mp4"
    output_path = os.path.join(CACHE_DIR, clip_id)

    if not os.path.exists(output_path) or not is_clip_cached(episode_path, start_time, end_time, output_path):
        extract_clip(episode_path, start_time, end_time, output_path)

    return output_path
def clear_cache_by_age_and_limit(max_age_days=90, max_files=20000):
    current_time = time.time()
    files = [(f, os.path.getctime(os.path.join(CACHE_DIR, f))) for f in os.listdir(CACHE_DIR) if not f.endswith('.json')]
    files.sort(key=lambda x: x[1])

    while files and (len(files) > max_files or (current_time - files[0][1]) / (60 * 60 * 24) > max_age_days):
        os.remove(os.path.join(CACHE_DIR, files[0][0]))
        if os.path.exists(os.path.join(CACHE_DIR, files[0][0] + '.json')):
            os.remove(os.path.join(CACHE_DIR, files[0][0] + '.json'))
        files.pop(0)
def cache_clip_metadata(episode_path, start_time, end_time, output_path):
    metadata_path = output_path + '.json'
    metadata = {'episode_path': episode_path, 'start_time': start_time, 'end_time': end_time}
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
def is_clip_cached(episode_path, start_time, end_time, output_path):
    metadata_path = output_path + '.json'
    if not os.path.exists(metadata_path):
        return False
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata['episode_path'] == episode_path and metadata['start_time'] == start_time and metadata['end_time'] == end_time
def extract_clip(episode_path, start_time, end_time, output_path):
    adjusted_start_time = max(int(start_time) - 2, 0)
    adjusted_end_time = int(end_time) + 2
    cmd = ["ffmpeg", "-y", "-ss", str(adjusted_start_time), "-i", episode_path, "-t", str(adjusted_end_time - adjusted_start_time),
           "-c:v", "libx264", "-crf", "25", "-profile:v", "main", "-c:a", "aac", "-b:a", "128k", "-ac", "2",
           "-preset", "superfast", "-movflags", "+faststart", "-loglevel", "error", "-reset_timestamps", "1", output_path]
    subprocess.run(cmd, check=True)
    cache_clip_metadata(episode_path, adjusted_start_time, adjusted_end_time, output_path)
def compile_clips_into_one(segments, chat_id, bot):
    files_to_compile = []

    for segment in segments:
        clip_path = download_and_cache_clip(segment)
        if clip_path:
            files_to_compile.append(clip_path)

    if not files_to_compile:
        bot.send_message(chat_id, "Nie udało się pobrać klipów wideo.")
        return

    output_file = f"compiled_{chat_id}.mp4"

    # Create a temporary text file for ffmpeg concatenation
    with open("concat_list.txt", "w") as file:
        for clip_path in files_to_compile:
            file.write(f"file '{clip_path}'\n")

    compile_command = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_list.txt",
        "-c", "copy", output_file
    ]

    try:
        subprocess.run(compile_command, check=True)
        # Check the size of the output file
        output_file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        if output_file_size_mb > 49:
            # Compress the file if it's larger than 49MB
            compressed_output_file = f"compressed_{output_file}"
            compress_to_target_size(output_file, compressed_output_file)
            output_file = compressed_output_file  # Update the output file to the compressed one
        with open(output_file, 'rb') as file:
            bot.send_video(chat_id, file)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while compiling clips: {e}")
    finally:
        for file_path in files_to_compile:
            os.remove(file_path)
        os.remove(output_file)
        os.remove("concat_list.txt")  # Clean up the temporary file
def download_and_cache_clip(segment):
    # Extract 'episode_path' from 'video_path' if 'file_path' is not in 'episode_info'
    if 'video_path' in segment:
        episode_path = segment['video_path']
    elif 'episode_info' in segment and 'file_path' in segment['episode_info']:
        episode_path = segment['episode_info']['file_path']
    else:
        print(f"Error: 'file_path' not found in segment and 'video_path' is missing. Segment data: {segment}")
        return None

    start_time = segment['start']
    end_time = segment['end']
    output_path = f"cache/season_{segment['episode_info']['season']}_" \
                  f"episode_{segment['episode_info']['episode_number']}_" \
                  f"{start_time}_{end_time}.mp4"

    if is_clip_cached(episode_path, start_time, end_time, output_path):
        return output_path

    adjusted_start_time = max(int(start_time) - 2, 0)
    adjusted_end_time = int(end_time) + 2

    try:
        cmd = [
            "ffmpeg", "-y", "-ss", str(adjusted_start_time), "-to", str(adjusted_end_time), "-i", episode_path,
            "-c:v", "libx264", "-crf", "25", "-profile:v", "main", "-c:a", "aac", "-b:a", "128k",
            "-ac", "2", "-preset", "superfast", "-movflags", "+faststart", "-loglevel", "error",
            "-reset_timestamps", "1", output_path
        ]
        subprocess.run(cmd, check=True)
        cache_clip_metadata(episode_path, adjusted_start_time, adjusted_end_time, output_path)
        print(f"Clip cached successfully: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to download and cache clip due to subprocess error: {e}")
        return None
def compress_to_target_size(input_file, output_file, target_size_mb=49, audio_bitrate_kbps=128):
    """
    Compresses a video file to a target size using the H.264 (libx264) codec, ensuring compatibility with specified devices.

    Parameters:
    - input_file: Path to the input video file.
    - output_file: Path where the output video will be saved.
    - target_size_mb: Target size of the output file in megabytes (MB).
    - audio_bitrate_kbps: Bitrate for the audio stream in kilobits per second (kbps).
    """
    video_duration = get_video_duration(input_file)
    if video_duration == 0:
        print("Error: Unable to retrieve video duration or video is empty.")
        return False

    # Calculate target total bitrate in kbps, taking into account the length of the video and desired target size.
    target_total_bitrate_kbps = (target_size_mb * 8 * 1024) / video_duration - audio_bitrate_kbps

    if target_total_bitrate_kbps < 1:
        print("Error: Target size too small for given video.")
        return False

    # Construct the ffmpeg command using the provided flags for compatibility.
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-c:v", "libx265", "-crf", "25", "-preset", "superfast",
        "-profile:v", "main",
        "-c:a", "aac", "-b:a", f"{audio_bitrate_kbps}k", "-ac", "2",
        "-b:v", f"{target_total_bitrate_kbps}k",
        "-movflags", "+faststart", "-loglevel", "error",
        "-reset_timestamps", "1", output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Video compressed and saved to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during video compression: {e}")
        return False

def get_video_duration(input_file):
    """
    Returns the duration of the video in seconds.

    Parameters:
    - input_file: Path to the video file.
    """
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during video duration retrieval: {e}")
        return 0