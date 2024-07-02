from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from bot.utils.db import is_user_authorized

class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        update: Update = event
        user_id = None

        if isinstance(update.message, Message):
            user_id = update.message.from_user.username
        elif isinstance(update.callback_query, CallbackQuery):
            user_id = update.callback_query.from_user.username

        if user_id is None or not await is_user_authorized(user_id):
            if user_id is not None:
                await update.message.answer("❌ Nie masz uprawnień do korzystania z tego bota. ❌")
            return

        return await handler(event, data)