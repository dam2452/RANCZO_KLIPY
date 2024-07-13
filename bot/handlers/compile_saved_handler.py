import logging
import os
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager
from bot.utils.functions import (
    compile_clips,
    send_compiled_clip,
)


class CompileSelectedClipsHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['polaczklipy', 'concatclips', 'pk']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/polaczklipy {message.text}")
        username = message.from_user.username

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            await self.__reply_no_clip_names_provided(message)
            return

        clip_names = content[1:]
        selected_clips_data = []

        for clip_name in clip_names:
            clip = await DatabaseManager.get_clip_by_name(username, clip_name)
            if not clip:
                await self.__reply_clip_not_found(message, clip_name, username)
                return
            selected_clips_data.append(clip[0])

        if not selected_clips_data:
            await self.__reply_no_matching_clips_found(message)
            return

        try:
            compiled_output = await compile_clips(selected_clips_data, self._bot)
            await send_compiled_clip(chat_id, compiled_output, self._bot)
            await self.__clean_up_temp_files(compiled_output, selected_clips_data)

            await self._log_system_message(
                logging.INFO,
                f"Compiled clip sent to user '{username}' and temporary files removed.",
            )
        except Exception as e:
            await self.__reply_compilation_error(message, e)

    @staticmethod
    async def __clean_up_temp_files(compiled_output: str, selected_clips_data) -> None:
        for temp_file in selected_clips_data:
            os.remove(temp_file)
        os.remove(compiled_output)

    async def __reply_no_clip_names_provided(self, message: Message) -> None:
        await message.answer("📄 Podaj nazwy klipów do skompilowania w odpowiedniej kolejności.")
        await self._log_system_message(logging.INFO, "No clip names provided by user.")

    async def __reply_clip_not_found(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(f"❌ Nie znaleziono klipu o nazwie '{clip_name}'.")
        await self._log_system_message(logging.INFO, f"Clip '{clip_name}' not found for user '{username}'.")

    async def __reply_no_matching_clips_found(self, message: Message) -> None:
        await message.answer("❌ Nie znaleziono pasujących klipów do kompilacji.")
        await self._log_system_message(logging.INFO, "No matching clips found for compilation.")

    async def __reply_compilation_error(self, message: Message, exception: Exception) -> None:
        await message.answer("⚠️ Wystąpił błąd podczas kompilacji klipów.⚠️")
        await self._log_system_message(logging.ERROR, f"An error occurred while compiling clips: {exception}")
