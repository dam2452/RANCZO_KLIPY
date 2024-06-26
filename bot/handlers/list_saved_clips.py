import logging
from aiogram import Router, Bot, types, Dispatcher
from aiogram.filters import Command
from bot.utils.db import get_saved_clips
from tabulate import tabulate

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("mojeklipy"))
async def list_saved_clips(message: types.Message, bot: Bot):
    username = message.from_user.username
    if not username:
        await message.answer("Nie można zidentyfikować użytkownika.")
        return

    clips = await get_saved_clips(username)
    if not clips:
        await message.answer("Nie masz zapisanych klipów.")
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
            episode_number_mod = episode_number % 13
            if episode_number_mod == 0:
                episode_number_mod = 13
            season_episode = f"S{season:02d}E{episode_number_mod:02d}"

        table_data.append([idx, clip_name, season_episode, length_str])

    table = tabulate(table_data, headers=["#", "Nazwa Klipu", "Sezon/Odcinek", "Długość"], tablefmt="grid")
    response_message = f"Twoje zapisane klipy:\n\n<pre>{table}</pre>"
    await message.answer(response_message, parse_mode="HTML")

def register_list_clips_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
