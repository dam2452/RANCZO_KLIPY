import logging
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from bot.utils.db import DatabaseManager
from tabulate import tabulate
from datetime import date
from bot.middlewares.authorization import AuthorizationMiddleware
from bot.middlewares.error_handler import ErrorHandlerMiddleware

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("mojeklipy"))
async def list_saved_clips(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        if not username or not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie można zidentyfikować użytkownika lub brak uprawnień.❌")
            logger.warning("User identification failed or user not authorized.")
            return

        clips = await DatabaseManager.get_saved_clips(username)
        if not clips:
            await message.answer("📭 Nie masz zapisanych klipów.📭")
            logger.info(f"No saved clips found for user: {username}")
            return

        table_data = []
        for idx, (clip_name, start_time, end_time, season, episode_number, is_compilation) in enumerate(clips, start=1):
            length = end_time - start_time if end_time and start_time is not None else None
            if length:
                minutes, seconds = divmod(length, 60)
                length_str = f"{minutes}m{seconds}s" if minutes else f"{seconds}s"
            else:
                length_str = "Brak danych"

            if is_compilation or season is None or episode_number is None:
                season_episode = "Kompilacja"
            else:
                episode_number_mod = (episode_number - 1) % 13 + 1  # Convert to episode number within the season
                season_episode = f"S{season:02d}E{episode_number_mod:02d}"

            table_data.append([idx, clip_name, season_episode, length_str])

        table = tabulate(table_data, headers=["#", "Nazwa Klipu", "Sezon/Odcinek", "Długość"], tablefmt="grid")
        response_message = f"""
🎬 Twoje Zapisane Klipy 🎬

🎥 Użytkownik: @{username}
📅 Data: {date.today().strftime('%Y-%m-%d')}

<pre>{table}</pre>

Dziękujemy wspieranie projektu 🌟
"""
        await message.answer(response_message, parse_mode="HTML")
        logger.info(f"List of saved clips sent to user '{username}'.")

    except Exception as e:
        logger.error(f"Error handling /mojeklipy command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")

def register_list_clips_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
