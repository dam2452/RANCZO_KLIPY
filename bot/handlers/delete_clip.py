import logging
from aiogram import Router, types, Dispatcher
from aiogram.filters import Command
from bot.utils.db import delete_clip

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("usunklip"))
async def delete_saved_clip(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer("❌ Nie można zidentyfikować użytkownika.")
        return

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer("❌ Podaj nazwę klipu do usunięcia. Przykład: /usunklip nazwa_klipu")
        return

    clip_name = command_parts[1]
    result = await delete_clip(username, clip_name)

    if result == "DELETE 0":
        await message.answer(f"🚫 Klip o nazwie '{clip_name}' nie istnieje.")
    else:
        await message.answer(f"✅ Klip o nazwie '{clip_name}' został usunięty.")


def register_delete_clip_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
