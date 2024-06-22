import ffmpeg

def convert_time_to_seconds(time_str):
    """
    Converts time in HH:MM:SS.xxx format to seconds.

    Parameters:
    - time_str (str): Time string in HH:MM:SS.xxx format.

    Returns:
    - float: Time in seconds.
    """
    h, m, s = time_str.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + float(ms) / 1000
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
def extract_clip(episode_path, start_time, end_time, output_path):
    """
    Extracts a clip from a video file using ffmpeg.

    This function adjusts the start and end times by subtracting 2 seconds from the start time
    and adding 2 seconds to the end time to ensure no content is missed. The extracted clip
    is copied without re-encoding to ensure quick extraction.

    Parameters:
    - episode_path (str): Path to the video file.
    - start_time (str): The start time of the clip in HH:MM:SS.xxx format.
    - end_time (str): The end time of the clip in HH:MM:SS.xxx format.
    - output_path (str): The path to save the extracted clip.
    """
    # Convert start and end times to seconds
    start_time_seconds = convert_time_to_seconds(start_time)
    end_time_seconds = convert_time_to_seconds(end_time)

    # Adjust start and end times to capture a bit more content
    adjusted_start_time = max(start_time_seconds - 2, 0)
    adjusted_end_time = end_time_seconds + 2

    # Calculate the duration
    duration = adjusted_end_time - adjusted_start_time

    # Use ffmpeg to extract and copy the clip without re-encoding
    try:
        (
            ffmpeg
            .input(episode_path, ss=adjusted_start_time, t=duration)
            .output(output_path,
                    c='copy',
                    movflags='+faststart',
                    fflags='+genpts',
                    loglevel='error')
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print(f"Error occurred during clip extraction: {e}")

#extract_clip(r"RANCZO-WIDEO/Sezon 10/Ranczo_S10E01.mp4", '00:01:23.456', '00:2:23.456', 'outputTEST2.mp4')
#print(get_video_duration(r"RANCZO-WIDEO/Sezon 1/Ranczo_S01E01.mp4"))
#compress_to_target_size(r"outputTEST.mp4", 'outputTESTpokomprsjiDO49_defaultAUDIO.mp4', 49)
extract_clip(r"Ranczo_S10E01_TEST_JAKOs_BOTAcq28.mp4", '00:01:23.456', '00:2:23.456', 'outputTEST28888.mp4')
