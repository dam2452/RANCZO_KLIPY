import io
import logging
from ..video_processing import extract_clip, convert_seconds_to_time_str, convert_time_to_seconds


logger = logging.getLogger(__name__)

def send_clip_to_telegram(bot, chat_id, video_path, start_time, end_time):
    """
    Extract a video clip and send it to the Telegram user.
    """
    try:
        # Convert start and end times to strings
        start_time_str = convert_seconds_to_time_str(start_time)
        end_time_str = convert_seconds_to_time_str(end_time)

        # Extract the clip to memory
        out_buf = io.BytesIO()
        out_buf.name = "clip.mp4"
        extract_clip(video_path, start_time_str, end_time_str, out_buf)

        # Send the clip
        out_buf.seek(0)
        bot.send_video(chat_id, out_buf)
        logger.info(f"Sent video clip from {start_time_str} to {end_time_str} to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send video clip: {e}")