import os
import time
import json
import subprocess
from cachetools.func import ttl_cache

# Constants
CACHE_DIR = os.path.join(os.getcwd(), "cache")

# Ensure the cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

@ttl_cache(maxsize=100, ttl=3600)
def get_cached_clip_path(episode_path, start_time, end_time):
    """Retrieve or generate a cached clip path."""
    clip_id = f"{os.path.basename(episode_path)}_{start_time}_{end_time}.mp4"
    output_path = os.path.join(CACHE_DIR, clip_id)

    if not os.path.exists(output_path):
        extract_clip(episode_path, start_time, end_time, output_path)

    return output_path

def clear_cache_by_age_and_limit(max_age_days=90, max_files=20000):
    """Clear cache based on age and limit constraints."""
    current_time = time.time()
    files_and_times = []

    for filename in os.listdir(CACHE_DIR):
        if filename.endswith('.json'):
            continue  # Skip metadata files

        filepath = os.path.join(CACHE_DIR, filename)
        file_creation_time = os.path.getctime(filepath)
        age_days = (current_time - file_creation_time) / (60 * 60 * 24)
        files_and_times.append((filepath, file_creation_time, age_days))

    # Sort by oldest first
    files_and_times.sort(key=lambda x: x[1])

    # Remove old files
    for filepath, _, age_days in files_and_times:
        if age_days > max_age_days or len(files_and_times) > max_files:
            os.remove(filepath)
            metadata_path = filepath + '.json'
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            files_and_times.remove((filepath, _, age_days))  # Update list

def cache_clip_metadata(episode_path, start_time, end_time, output_path):
    """Cache metadata for a clip."""
    metadata_path = output_path + '.json'
    metadata = {
        'episode_path': episode_path,
        'start_time': start_time,
        'end_time': end_time
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

def is_clip_cached(episode_path, start_time, end_time, output_path):
    """Check if a clip is already cached."""
    metadata_path = output_path + '.json'
    if not os.path.exists(metadata_path) or not os.path.exists(output_path):
        return False
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return (metadata['episode_path'] == episode_path and
            metadata['start_time'] == start_time and
            metadata['end_time'] == end_time)

def extract_clip(episode_path, start_time, end_time, output_path):
    """Extract a video clip, adjusting times slightly to avoid cuts."""
    adjusted_start_time = max(int(start_time) - 2, 0)
    adjusted_end_time = int(end_time) + 2

    if is_clip_cached(episode_path, adjusted_start_time, adjusted_end_time, output_path):
        print("Clip is already cached. Skipping extraction.")
        return True

    try:
        cmd = [
            "ffmpeg", "-y", "-ss", str(adjusted_start_time), "-i", episode_path,
            "-t", str(adjusted_end_time - adjusted_start_time), "-c:v", "libx264",
            "-crf", "25", "-profile:v", "main", "-c:a", "aac", "-b:a", "128k",
            "-ac", "2", "-preset", "superfast", "-movflags", "+faststart",
            "-loglevel", "error", output_path
        ]
        subprocess.run(cmd, check=True)
        cache_clip_metadata(episode_path, adjusted_start_time, adjusted_end_time, output_path)
        print(f"Clip extracted and cached: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while extracting clip: {e}")
        return False

    return True
