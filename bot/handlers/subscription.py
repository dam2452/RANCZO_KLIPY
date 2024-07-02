import logging
from datetime import date
from aiogram import Router, Dispatcher, types, Bot
from aiogram.filters import Command
from bot.utils.db import get_user_subscription, is_user_authorized

logger = logging.getLogger(__name__)
router = Router()

class UserManager:
    @staticmethod
    async def get_subscription_status(username: str):
        subscription_end = await get_user_subscription(username)
        if subscription_end is None:
            return None
        days_remaining = (subscription_end - date.today()).days
        return subscription_end, days_remaining

@router.message(Command('subskrypcja'))
async def check_subscription(message: types.Message, bot: Bot):
    username = message.from_user.username
    if not username or not await is_user_authorized(username):
        await message.answer("❌ Nie można zidentyfikować użytkownika lub brak uprawnień.")
        logger.warning("User identification failed or user not authorized.")
        return

    subscription_status = await UserManager.get_subscription_status(username)
    if subscription_status is None:
        await message.answer("🚫 Nie masz aktywnej subskrypcji.")
        logger.info(f"No active subscription found for user '{username}'.")
        return

    subscription_end, days_remaining = subscription_status
    response = f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""
    await message.answer(response, parse_mode='Markdown')
    logger.info(f"Subscription status sent to user '{username}'.")

def register_subscription_handler(dispatcher: Dispatcher):
    dispatcher.include_router(router)
