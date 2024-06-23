import ffmpeg
import tempfile
import os

def convert_time_to_seconds(time_str):
    """
    Convert a time string to seconds. Handles formats:
    - HH:MM:SS
    - MM:SS
    - SS.xxx
    """
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
    """
    Converts time in seconds to HH:MM:SS.xxx format.

    Parameters:
    - seconds (float): Time in seconds.

    Returns:
    - str: Time string in HH:MM:SS.xxx format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
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
        print(f"Error occurred during video duration retrieval: {e}")
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
        print("Error: Unable to retrieve video duration or video is empty.")
        return False

    video_duration = convert_time_to_seconds(formatted_duration)

    # Calculate target total bitrate in kbps, taking into account the length of the video and desired target size.
    target_total_bitrate_kbps = (target_size_mb * 8 * 1024) / video_duration

    if target_total_bitrate_kbps < 1:
        print("Error: Target size too small for given video.")
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
        print(f"Video compressed to {target_size_mb}MB and saved to {output_file}")
        return True
    except ffmpeg.Error as e:
        print(f"Error occurred during video compression: {e}")
        return False
def extract_clip(episode_path, start_time, end_time, output):
    """
    Extracts a clip from a video file using ffmpeg.

    This function adjusts the start and end times by subtracting 2 seconds from the start time
    and adding 2 seconds to the end time to ensure no content is missed. The extracted clip
    is copied without re-encoding to ensure quick extraction.

    Parameters:
    - episode_path (str): Path to the video file.
    - start_time (str): The start time of the clip in HH:MM:SS.xxx format.
    - end_time (str): The end time of the clip in HH:MM:SS.xxx format.
    - output (io.BytesIO): The io.BytesIO object to save the extracted clip.
    """
    # Convert start and end times to seconds
    start_time_seconds = convert_time_to_seconds(start_time)
    end_time_seconds = convert_time_to_seconds(end_time)

    # Adjust start and end times to capture a bit more content
    adjusted_start_time = max(start_time_seconds - 2, 0)
    adjusted_end_time = end_time_seconds + 2

    # Calculate the duration
    duration = adjusted_end_time - adjusted_start_time

    # Log the details for debugging
    print(f"Extracting clip from: {episode_path}")
    print(f"Start time (seconds): {start_time_seconds}, Adjusted start time: {adjusted_start_time}")
    print(f"End time (seconds): {end_time_seconds}, Adjusted end time: {adjusted_end_time}")
    print(f"Duration: {duration}")

    # Use a temporary file for the extraction
    with tempfile.NamedTemporaryFile(delete=False, dir=os.path.expanduser('~')) as temp_file:
        temp_filename = temp_file.name

    try:
        (
            ffmpeg
            .input(episode_path, ss=adjusted_start_time, t=duration)
            .output(temp_filename, format='mp4', c='copy', movflags='+faststart', fflags='+genpts')
            .run(overwrite_output=True)
        )

        # Read the content of the temporary file into the output buffer
        with open(temp_filename, 'rb') as f:
            output.write(f.read())

    except ffmpeg.Error as e:
        error_output = e.stderr.decode() if e.stderr else str(e)
        print(f"Error occurred during clip extraction: {error_output}")

    finally:
        # Clean up the temporary file
        os.remove(temp_filename)

# Example usage:
#extract_clip(r"RANCZO-WIDEO/Sezon 10/Ranczo_S10E01.mp4", '00:01:23.456', '00:2:23.456', 'outputTEST2.mp4')
#print(get_video_duration(r"RANCZO-WIDEO/Sezon 1/Ranczo_S01E01.mp4"))
#compress_to_target_size(r"outputTEST.mp4", 'outputTESTpokomprsjiDO49_defaultAUDIO.mp4', 49)
# extract_clip(r"Ranczo_S10E01_TEST_JAKOs_BOTAcq28.mp4", '00:01:23.456', '00:2:23.456', 'outputTEST28888.mp4')
