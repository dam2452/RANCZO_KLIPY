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
    """Get or create a cached clip path.

    Parameters:
        episode_path (str): Path to the episode file.
        start_time (int): Start time of the clip.
        end_time (int): End time of the clip.

    Returns:
        str: The path to the cached clip.
    """
    clip_id = f"{os.path.basename(episode_path)}_{start_time}_{end_time}.mp4"
    output_path = os.path.join(CACHE_DIR, clip_id)
    if not os.path.exists(output_path) or not is_clip_cached(episode_path, start_time, end_time, output_path):
        extract_clip(episode_path, start_time, end_time, output_path)
    return output_path
def clear_cache_by_age_and_limit(max_age_days=90, max_files=20000):
    """
    Remove files from the cache directory based on age and limit constraints.
    Only non-JSON files are considered, but if such a file is deleted, its
    corresponding JSON file (if exists) is also deleted.

    :param max_age_days: Maximum age of files to retain.
    :param max_files: Maximum number of files to retain.
    """
    # Current time in seconds
    current_time = time.time()

    # List of tuples (filename, creation time) for non-JSON files
    cache_dir_files = [
        (filename, os.path.getctime(os.path.join(CACHE_DIR, filename)))
        for filename in os.listdir(CACHE_DIR) if not filename.endswith('.json')
    ]

    # Sort files by creation time (oldest first)
    cache_dir_files.sort(key=lambda file_info: file_info[1])

    while cache_dir_files:
        oldest_file, oldest_file_ctime = cache_dir_files[0]
        age_days = (current_time - oldest_file_ctime) / (60 * 60 * 24)

        # Exit loop if file count and age constraints are met
        if len(cache_dir_files) <= max_files and age_days <= max_age_days:
            break

        # Attempt to remove the oldest file
        try:
            os.remove(os.path.join(CACHE_DIR, oldest_file))
            print(f"Removed: {oldest_file}")
            json_file_path = os.path.join(CACHE_DIR, oldest_file + '.json')
            # Check and remove the corresponding JSON file if it exists
            if os.path.exists(json_file_path):
                os.remove(json_file_path)
                print(f"Removed corresponding JSON file: {oldest_file + '.json'}")
        except OSError as e:
            print(f"Error removing file {oldest_file}: {e}")
        finally:
            # Remove the processed file from the list regardless of success or failure
            cache_dir_files.pop(0)
def cache_clip_metadata(episode_path, start_time, end_time, output_path):
    """Cache metadata for a clip.

    Parameters:
        episode_path (str): Path to the episode file.
        start_time (int): Start time of the clip.
        end_time (int): End time of the clip.
        output_path (str): Path to the output clip file.
    """
    metadata_path = f"{output_path}.json"
    metadata = {'episode_path': episode_path, 'start_time': start_time, 'end_time': end_time}
    with open(metadata_path, 'w') as file:
        json.dump(metadata, file)
def is_clip_cached(episode_path, start_time, end_time, output_path):
    """Check if a clip is already cached.

    Parameters:
        episode_path (str): Path to the episode file.
        start_time (int): Start time of the clip.
        end_time (int): End time of the clip.
        output_path (str): Path to the output clip file.

    Returns:
        bool: True if the clip is cached, False otherwise.
    """
    metadata_path = f"{output_path}.json"
    if not os.path.exists(metadata_path):
        return False
    with open(metadata_path) as file:
        metadata = json.load(file)
    return (metadata['episode_path'] == episode_path and
            metadata['start_time'] == start_time and
            metadata['end_time'] == end_time)
def extract_clip(episode_path, start_time, end_time, output_path):
    """
    Extracts a clip from a video file using ffmpeg.

    This function adjusts the start and end times by subtracting 2 seconds from the start time
    and adding 2 seconds to the end time to ensure no content is missed. The extracted clip
    is encoded using H.264 video codec and AAC audio codec, with specific quality and speed settings.

    Parameters:
    - episode_path (str): Path to the video file.
    - start_time (int): The start time of the clip in seconds.
    - end_time (int): The end time of the clip in seconds.
    - output_path (str): The path to save the extracted clip.
    """
    # Adjust start and end times to capture a bit more content
    adjusted_start_time = max(int(start_time) - 2, 0)
    adjusted_end_time = int(end_time) + 2

    # Prepare the ffmpeg command for extracting and encoding the clip
    ffmpeg_cmd = [
        "ffmpeg", "-y",  # Overwrite output files without asking
        "-ss", str(adjusted_start_time),  # Start time
        "-i", episode_path,  # Input file
        "-t", str(adjusted_end_time - adjusted_start_time),  # Duration
        "-c:v", "libx264", "-crf", "25",  # Video codec and quality settings
        "-profile:v", "main",  # H.264 profile
        "-c:a", "aac", "-b:a", "128k",  # Audio codec and bitrate
        "-ac", "2",  # Audio channels
        "-preset", "superfast",  # Encoding speed/quality trade-off
        "-vf", "yadif=0:-1:0,scale=1920:1080",  # Deinterlace and scale video
        "-movflags", "+faststart",  # Optimize for streaming
        "-loglevel", "error",  # Only show error messages
        "-reset_timestamps", "1",  # Reset timestamps
        output_path  # Output file
    ]

    # Execute the ffmpeg command
    subprocess.run(ffmpeg_cmd, check=True)

    # Optionally, cache metadata about the extracted clip
    cache_clip_metadata(episode_path, adjusted_start_time, adjusted_end_time, output_path)
def compile_clips_into_one(segments, chat_id, bot):
    """
    Compiles multiple video clips into one file and sends it via a bot.

    :param segments: A list of segments to be downloaded and compiled.
    :param chat_id: ID of the chat to send the compiled video to.
    :param bot: The bot instance used for sending messages and videos.
    """
    files_to_compile = [download_and_cache_clip(segment) for segment in segments if download_and_cache_clip(segment)]

    if not files_to_compile:
        bot.send_message(chat_id, "Nie udało się pobrać klipów wideo.")
        return

    output_file = f"compiled_{chat_id}.mp4"

    try:
        # Use a temporary file to list the clips to be concatenated
        with open("concat_list.txt", "w") as file:
            for clip_path in files_to_compile:
                file.write(f"file '{clip_path}'\n")

        # Compile clips into one file
        compile_command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_list.txt", "-c", "copy", output_file]
        subprocess.run(compile_command, check=True)

        # Optionally compress the compiled video
        output_file_size_mb = os.path.getsize(output_file) / (1024 ** 2)
        if output_file_size_mb > 49:
            compressed_output_file = f"compressed_{output_file}"
            compress_to_target_size(output_file, compressed_output_file)
            output_file = compressed_output_file

        # Send the video
        with open(output_file, 'rb') as file:
            bot.send_video(chat_id, file)

    except subprocess.CalledProcessError as e:
        bot.send_message(chat_id, f"Wystąpił błąd podczas kompilacji klipów: {e}")
    finally:
        # Clean up: Remove downloaded clips and any temporary files
        for file_path in set(files_to_compile + ["concat_list.txt", output_file]):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Ignore errors from deleting files that may not exist
def download_and_cache_clip(segment):
    """
    Downloads and caches a video clip based on the provided segment information.

    The function checks if the clip is already cached. If not, it uses FFmpeg to download and cache the clip.
    It adjusts the start and end times by 2 seconds to ensure no content is missed due to timing inaccuracies.

    Parameters:
    - segment (dict): A dictionary containing segment information, including start and end times,
                      episode info, and video path.

    Returns:
    - str or None: The path to the cached clip if successful, or None if an error occurs.
    """
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
    Compresses a video file to a target size using the H.265 (libx265) codec, ensuring compatibility with specified devices.
    The video is standardized to 1080p resolution and deinterlaced if necessary.

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

    # Construct the ffmpeg command with deinterlacing (yadif filter) and scaling to 1080p
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-c:v", "libx265", "-crf", "29", "-preset", "superfast",
        "-vf", "yadif=0:-1:0,scale=1920:1080",  # Deinterlace and scale to 1080p
        "-c:a", "aac", "-b:a", f"{audio_bitrate_kbps}k", "-ac", "2",
        "-b:v", f"{target_total_bitrate_kbps}k",
        "-movflags", "+faststart", "-loglevel", "error",
        "-reset_timestamps", "1", output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Video compressed to {target_size_mb}MB and saved to {output_file}")
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