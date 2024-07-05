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

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command(commands=['usunklip', 'deleteclip','uk']))
async def delete_saved_clip(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        if not username or not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie masz uprawnień do korzystania z tego bota.❌")
            logger.warning("Unauthorized access attempt: Unable to identify user or user not authorized.")
            await DatabaseManager.log_system_message("WARNING", "Unauthorized access attempt: Unable to identify user or user not authorized.")
            return

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.answer("❌ Podaj nazwę klipu do usunięcia. Przykład: /usunklip nazwa_klipu ❌")
            logger.info("No clip name provided by user.")
            await DatabaseManager.log_system_message("INFO", "No clip name provided by user.")
            return

        clip_name = command_parts[1]
        logger.info(f"User '{username}' requested deletion of clip: '{clip_name}'")
        await DatabaseManager.log_user_activity(username, f"/usunklip {clip_name}")

        result = await DatabaseManager.delete_clip(username, clip_name)

        if result == "DELETE 0":
            await message.answer(f"🚫 Klip o nazwie '{clip_name}' nie istnieje.🚫")
            logger.info(f"Clip '{clip_name}' does not exist for user '{username}'.")
            await DatabaseManager.log_system_message("INFO", f"Clip '{clip_name}' does not exist for user '{username}'.")
        else:
            await message.answer(f"✅ Klip o nazwie '{clip_name}' został usunięty.✅")
            logger.info(f"Clip '{clip_name}' has been successfully deleted for user '{username}'.")
            await DatabaseManager.log_system_message("INFO", f"Clip '{clip_name}' has been successfully deleted for user '{username}'.")

    except Exception as e:
        logger.error(f"Error handling /usunklip command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error handling /usunklip command for user '{message.from_user.username}': {e}")

def register_delete_clip_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)

# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
