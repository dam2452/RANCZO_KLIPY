import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager


class DeleteClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['usunklip', 'deleteclip', 'uk']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/usunklip {message.text}")
        username = message.from_user.username

        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return await self.__reply_no_clip_name_provided(message)

        clip_name = command_parts[1]

        result = await DatabaseManager.delete_clip(username, clip_name)

        if result == "DELETE 0":
            await self.__reply_clip_not_exist(message, clip_name, username)
        else:
            await self.__reply_clip_deleted(message, clip_name, username)

    async def __reply_no_clip_name_provided(self, message: Message) -> None:
        await message.answer("❌ Podaj nazwę klipu do usunięcia. Przykład: /usunklip nazwa_klipu ❌")
        await self._log_system_message(logging.INFO, "No clip name provided by user.")

    async def __reply_clip_not_exist(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(f"🚫 Klip o nazwie '{clip_name}' nie istnieje.🚫")
        await self._log_system_message(logging.INFO, f"Clip '{clip_name}' does not exist for user '{username}'.")

    async def __reply_clip_deleted(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(f"✅ Klip o nazwie '{clip_name}' został usunięty.✅")
        await self._log_system_message(
            logging.INFO,
            f"Clip '{clip_name}' has been successfully deleted for user '{username}'.",
        )
