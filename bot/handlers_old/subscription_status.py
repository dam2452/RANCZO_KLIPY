from datetime import date
import logging
from typing import (
    Optional,
    Tuple,
)

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


class UserManager:
    @staticmethod
    async def get_subscription_status(username: str) -> Optional[Tuple[date, int]]:
        subscription_end = await DatabaseManager.get_user_subscription(username)
        if subscription_end is None:
            return None
        days_remaining = (subscription_end - date.today()).days
        return subscription_end, days_remaining


@router.message(Command(commands=['subskrypcja', 'sub', 's']))
async def check_subscription(message: types.Message, bot: Bot) -> None:
    try:
        username = message.from_user.username

        subscription_status = await UserManager.get_subscription_status(username)
        if subscription_status is None:
            await message.answer("🚫 Nie masz aktywnej subskrypcji.🚫")
            logger.info(f"No active subscription found for user '{username}'.")
            await DatabaseManager.log_system_message("INFO", f"No active subscription found for user '{username}'.")
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
        await DatabaseManager.log_system_message("INFO", f"Subscription status sent to user '{username}'.")

    except Exception as e:
        logger.error(f"Error in check_subscription for user '{message.from_user.username}': {e}", exc_info=True)
        await message.answer("⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️")
        await DatabaseManager.log_system_message("ERROR", f"Error in check_subscription for user '{message.from_user.username}': {e}")


def register_subscription_handler(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)


router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
