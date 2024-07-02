import logging
from datetime import date
from aiogram import Router, Dispatcher, types, Bot
from aiogram.filters import Command
from bot.utils.db import add_report, is_user_authorized

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('report'))
async def handle_report(message: types.Message, bot: Bot):
    try:
        username = message.from_user.username
        if not username or not await is_user_authorized(username):
            await message.answer("❌ Nie można zidentyfikować użytkownika lub brak uprawnień.")
            logger.warning("User identification failed or user not authorized.")
            return

        report_content = message.text.split(maxsplit=1)
        if len(report_content) < 2:
            await message.answer("❌ Podaj treść raportu.")
            logger.info(f"No report content provided by user '{username}'.")
            return

        report = report_content[1]
        await add_report(username, report)
        await message.answer("✅ Dziękujemy za zgłoszenie. Twój raport został zapisany. 📄")
        logger.info(f"Report received from user '{username}': {report}")

    except Exception as e:
        logger.error(f"Error handling /report command for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania.")

def register_report_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
