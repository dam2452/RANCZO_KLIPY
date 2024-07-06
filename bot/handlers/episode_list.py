import logging

from aiogram import (
    Bot,
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command

from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware
from bot.utils.database import DatabaseManager
from bot.utils.transcription_search import SearchTranscriptions

logger = logging.getLogger(__name__)
router = Router()


def adjust_episode_number(absolute_episode) -> tuple[int, int] or None:
    """ Adjust the absolute episode number to season and episode format """
    season = (absolute_episode - 1) // 13 + 1
    episode = (absolute_episode - 1) % 13 + 1
    return season, episode


def split_message(message, max_length=4096) -> list[str] or str or None:
    """ Splits a message into chunks to fit within the Telegram message length limit """
    parts = []
    while len(message) > max_length:
        split_at = message.rfind('\n', 0, max_length)
        if split_at == -1:
            split_at = max_length
        parts.append(message[:split_at])
        message = message[split_at:].lstrip()
    parts.append(message)
    return parts


@router.message(Command(commands=['odcinki', 'episodes', 'o']))
async def handle_episode_list_command(message: types.Message, bot: Bot) -> None:
    try:
        search_transcriptions = SearchTranscriptions(router)
        content = message.text.split()
        if len(content) != 2:
            await message.answer(
                "📋 Podaj poprawną komendę w formacie: /listaodcinków <sezon>. Przykład: /listaodcinków 2",
            )
            logger.info("Incorrect command format provided by user.")
            await DatabaseManager.log_system_message("INFO", "Incorrect command format provided by user.")
            return

        season = int(content[1])

        # Pobieranie listy odcinków z Elasticsearch
        episodes = await search_transcriptions.find_episodes_by_season(season)
        if not episodes:
            await message.answer(f"❌ Nie znaleziono odcinków dla sezonu {season}.")
            logger.info(f"No episodes found for season {season}.")
            await DatabaseManager.log_system_message("INFO", f"No episodes found for season {season}.")
            return

        response = f"📃 Lista odcinków dla sezonu {season}:\n\n```\n"
        for episode in episodes:
            absolute_episode_number = episode['episode_number'] % 13
            if absolute_episode_number == 0:
                absolute_episode_number = 13
            _, _ = adjust_episode_number(absolute_episode_number)
            formatted_viewership = f"{episode['viewership']:,}".replace(',', '.')

            response += f"🎬 {episode['title']}: S{season:02d}E{absolute_episode_number:02d} ({episode['episode_number']}) \n"
            response += f"📅 Data premiery: {episode['premiere_date']}\n"
            response += f"👀 Oglądalność: {formatted_viewership}\n\n"

        # Split the response into smaller parts to avoid the Telegram message length limit
        response_parts = split_message(response)

        for part in response_parts:
            await message.answer(part + "```", parse_mode="Markdown")

        logger.info(f"Sent episode list for season {season} to user '{message.from_user.username}'.")
        await DatabaseManager.log_user_activity(message.from_user.username, f"/odcinki {season}")
        await DatabaseManager.log_system_message("INFO", f"Sent episode list for season {season} to user '{message.from_user.username}'.")

    except Exception as e:
        logger.error(f"An error occurred while handling episode list command: {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.")
        await DatabaseManager.log_system_message("ERROR", f"An error occurred while handling episode list command: {e}")


def register_episode_list_handler(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
