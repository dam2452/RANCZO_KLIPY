import logging
import os
import tempfile
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager
from bot.utils.video_manager import VideoManager


class SendClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['wyślij', 'wyslij', 'send', 'wys']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/wyślij {message.text}")
        username = message.from_user.username

        content = message.text.split()
        if len(content) < 2:
            return await self._reply_invalid_args_count(message, "📄 Podaj nazwę klipu. Przykład: /wyślij nazwa_klipu")

        clip_name = content[1]

        clip = await DatabaseManager.get_clip_by_name(username, clip_name)
        if not clip:
            return await self.__reply_clip_not_found(message, clip_name)

        video_data = clip[0]
        if not video_data:
            return await self.__reply_empty_clip_file(message, clip_name)

        temp_file_path = os.path.join(tempfile.gettempdir(), f"{clip_name}.mp4")

        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(video_data)

        if os.path.getsize(temp_file_path) == 0:
            return await self.__reply_empty_file_error(message, clip_name)

        await VideoManager.send_video(message.chat.id, temp_file_path, self._bot)

        os.remove(temp_file_path)
        await self._log_system_message(logging.INFO, f"Clip '{clip_name}' sent to user '{username}' and temporary file removed.")

    async def __reply_clip_not_found(self, message: Message, clip_name: str) -> None:
        await message.answer(f"❌ Nie znaleziono klipu o nazwie '{clip_name}'.❌")
        await self._log_system_message(
            logging.INFO,
            f"Clip '{clip_name}' not found for user '{message.from_user.username}'.",
        )

    async def __reply_empty_clip_file(self, message: Message, clip_name: str) -> None:
        await message.answer("⚠️ Plik klipu jest pusty.⚠️")
        await self._log_system_message(
            logging.WARNING,
            f"Clip file is empty for clip '{clip_name}' by user '{message.from_user.username}'.",
        )

    async def __reply_empty_file_error(self, message: Message, clip_name: str) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas wysyłania klipu. Plik jest pusty.⚠️")
        await self._log_system_message(
            logging.ERROR,
            f"File is empty after writing clip '{clip_name}' for user '{message.from_user.username}'.",
        )
