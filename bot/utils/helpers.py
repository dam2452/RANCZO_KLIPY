import logging

logger = logging.getLogger(__name__)

def send_clip_to_telegram(bot, chat_id, video_path, start_time, end_time):
    """
    Send the video clip to the Telegram user.
    """
    try:
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id, video)
        logger.info(f"Sent video clip from {start_time} to {end_time} to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send video clip: {e}")
