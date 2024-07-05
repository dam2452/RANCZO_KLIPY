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


@router.message(Command(commands=['report', 'zglos', 'r']))
async def handle_report(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        if not username or not await DatabaseManager.is_user_authorized(username):
            await message.answer("❌ Nie można zidentyfikować użytkownika lub brak uprawnień.❌")
            logger.warning("User identification failed or user not authorized.")
            await DatabaseManager.log_system_message("WARNING", "User identification failed or user not authorized.")
            return

        report_content = message.text.split(maxsplit=1)
        if len(report_content) < 2:
            await message.answer("❌ Podaj treść raportu.❌")
            logger.info(f"No report content provided by user '{username}'.")
            await DatabaseManager.log_system_message("INFO", f"No report content provided by user '{username}'.")
            return

        report = report_content[1]
        await DatabaseManager.add_report(username, report)
        await message.answer("✅ Dziękujemy za zgłoszenie. Twój raport został zapisany. 📄")
        logger.info(f"Report received from user '{username}': {report}")
        await DatabaseManager.log_user_activity(username, f"/report {report}")
        await DatabaseManager.log_system_message("INFO", f"Report received from user '{username}': {report}")

    except Exception as e:
        logger.error(f"Error handling /report command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error handling /report command for user '{message.from_user.username}': {e}")


def register_report_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
