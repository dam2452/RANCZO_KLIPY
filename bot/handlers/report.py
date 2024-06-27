from bot.utils.db import add_report
import logging
from datetime import date
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.db import get_user_subscription

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('report'))
async def handle_report(message: Message):
    username = message.from_user.username
    if not username:
        await message.answer("❌ Nie można zidentyfikować użytkownika.")
        return

    report_content = message.text.split(maxsplit=1)
    if len(report_content) < 2:
        await message.answer("❌ Podaj treść raportu.")
        return

    report = report_content[1]
    await add_report(username, report)
    await message.answer("✅ Dziękujemy za zgłoszenie. Twój raport został zapisany.")

def register_report_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
