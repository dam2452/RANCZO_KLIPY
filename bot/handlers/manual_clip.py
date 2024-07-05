import logging
import os

from aiogram import (
    Bot,
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command

from bot.utils.transcription_search import SearchTranscriptions
from bot.utils.video_handler import VideoManager

logger = logging.getLogger(__name__)
router = Router()


def minutes_str_to_seconds(time_str):
    """ Convert time string in the format MM:SS.ms to seconds """
    try:
        minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    except ValueError:
        return None


def adjust_episode_number(absolute_episode):
    """ Adjust the absolute episode number to season and episode format """
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode


@router.message(Command(commands=['wytnij', 'cut', 'wyt', 'pawlos']))  # XD pawlos
async def handle_manual_command(message: types.Message, bot: Bot):
    try:
        search_transcriptions = SearchTranscriptions(router)
        video_manager = VideoManager(bot)
        content = message.text.split()
        if len(content) != 4:
            await message.answer(
                "📋 Podaj poprawną komendę w formacie: /manual <sezon_odcinek> <czas_start> <czas_koniec>. Przykład: /manual S02E10 20:30.11",
            )
            logger.info("Incorrect command format provided by user.")
            return

        episode = content[1]  # Format: S02E10
        start_time = content[2]  # Format: 20:30.11
        end_time = content[3]  # Format: 21:32.50

        # Parse season and episode
        if episode[0] != 'S' or 'E' not in episode:
            await message.answer("❌ Błędny format sezonu i odcinka. Użyj formatu SxxExx. Przykład: S02E10")
            logger.info("Incorrect season/episode format provided by user.")
            return

        season = int(episode[1:3])
        episode_number = int(episode[4:6])

        # Calculate absolute episode number
        absolute_episode_number = (season - 1) * 13 + episode_number

        # Pobieranie ścieżki wideo z Elasticsearch
        video_path = await search_transcriptions.find_video_path_by_episode(season, absolute_episode_number)
        if not video_path or not os.path.exists(video_path):
            await message.answer("❌ Plik wideo nie istnieje dla podanego sezonu i odcinka.")
            logger.info(f"Video file does not exist: {video_path}")
            return

        # Calculate start and end time in seconds
        start_seconds = minutes_str_to_seconds(start_time)
        end_seconds = minutes_str_to_seconds(end_time)

        if start_seconds is None or end_seconds is None:
            await message.answer("❌ Błędny format czasu. Użyj formatu MM:SS.ms. Przykład: 20:30.11")
            logger.info("Incorrect time format provided by user.")
            return

        if end_seconds <= start_seconds:
            await message.answer("❌ Czas zakończenia musi być późniejszy niż czas rozpoczęcia.")
            logger.info("End time must be later than start time.")
            return

        # Extract and send clip using VideoManager
        await video_manager.extract_and_send_clip(message.chat.id, video_path, start_seconds, end_seconds)

    except Exception as e:
        logger.error(f"An error occurred while handling manual command: {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")


def register_manual_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
