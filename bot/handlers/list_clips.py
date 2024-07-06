import logging
from typing import Dict

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

logger = logging.getLogger(__name__)
router = Router()

number_to_emoji: Dict[str, str] = {
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',
}


def convert_number_to_emoji(number: int) -> str:
    return ''.join(number_to_emoji.get(digit, digit) for digit in str(number))


@router.message(Command(commands=['mojeklipy', 'myclips', 'mk']))
async def list_saved_clips(message: types.Message, bot: Bot) -> None:
    try:
        username = message.from_user.username
        if not username or not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie można zidentyfikować użytkownika lub brak uprawnień.❌")
            logger.warning("User identification failed or user not authorized.")
            await DatabaseManager.log_system_message("WARNING", "User identification failed or user not authorized.")
            return

        clips = await DatabaseManager.get_saved_clips(username)
        if not clips:
            await message.answer("📭 Nie masz zapisanych klipów.📭")
            logger.info(f"No saved clips found for user: {username}")
            await DatabaseManager.log_system_message("INFO", f"No saved clips found for user: {username}")
            return

        response = "🎬 Twoje Zapisane Klipy 🎬\n\n"
        response += f"🎥 Użytkownik: @{username}\n\n"
        clip_lines = []

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
                episode_number_mod = (episode_number - 1) % 13 + 1
                season_episode = f"S{season:02d}E{episode_number_mod:02d}"

            emoji_index = convert_number_to_emoji(idx)
            line1 = f"{emoji_index} | 📺 {season_episode} | 🕒 {length_str}"
            line2 = f"👉 {clip_name}"
            clip_lines.append(f"{line1} \n{line2}")

        response += "```\n" + "\n\n".join(clip_lines) + "\n```"
        await message.answer(response, parse_mode='Markdown')
        logger.info(f"List of saved clips sent to user '{username}'.")
        await DatabaseManager.log_user_activity(username, "/mojeklipy")
        await DatabaseManager.log_system_message("INFO", f"List of saved clips sent to user '{username}'.")

    except Exception as e:
        logger.error(f"Error handling /mojeklipy command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error handling /mojeklipy command for user '{message.from_user.username}': {e}")


def register_list_clips_handler(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
