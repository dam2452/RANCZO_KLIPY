import logging
from datetime import date
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.db import get_user_subscription

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('subskrypcja'))
async def check_subscription(message: Message):
    username = message.from_user.username
    if not username:
        await message.answer("❌ Nie można zidentyfikować użytkownika.")
        return

    subscription_end = await get_user_subscription(username)
    if subscription_end is None:
        await message.answer("🚫 Nie masz aktywnej subskrypcji.")
        return

    days_remaining = (subscription_end - date.today()).days
    response = f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""
    await message.answer(response, parse_mode='Markdown')

def register_subscription_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
