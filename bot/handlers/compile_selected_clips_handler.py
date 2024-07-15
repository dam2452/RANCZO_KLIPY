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
from bot.handlers.responses.compile_selected_clips_handler_responses import (
    get_invalid_args_count_message,
    get_no_matching_clips_found_message,
    get_clip_not_found_message,
    get_log_no_matching_clips_found_message,
    get_log_clip_not_found_message
)


class CompileSelectedClipsHandler(BotMessageHandler):
    class ClipNotFoundException(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def get_commands(self) -> List[str]:
        return ['polaczklipy', 'concatclips', 'pk']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/polaczklipy {message.text}")
        username = message.from_user.username

        chat_id = message.chat.id
        content = message.text.split()

        if len(content) < 2:
            return await self._reply_invalid_args_count(message, get_invalid_args_count_message())

        clip_names = content[1:]
        selected_clips_data = await self.__get_selected_clips_data(clip_names, username, message)

        if not selected_clips_data:
            return await self.__reply_no_matching_clips_found(message)

        compiled_output = await compile_clips(selected_clips_data)
        await send_compiled_clip(chat_id, compiled_output, self._bot)
        if os.path.exists(compiled_output):
            os.remove(compiled_output)

        await self.__clean_up_temp_files(selected_clips_data)

        await self._log_system_message(
            logging.INFO,
            f"Compiled clip sent to user '{username}' and temporary files removed.",
        )

    async def __get_selected_clips_data(self, clip_names: List[str], username: str, message: Message) -> List[bytes]:
        selected_clips_data = []
        for clip_name in clip_names:
            clip = await DatabaseManager.get_clip_by_name(username, clip_name)
            if not clip:
                await self.__reply_clip_not_found(message, clip_name, username)
            else:
                selected_clips_data.append(clip[0])
        return selected_clips_data

    @staticmethod
    async def __clean_up_temp_files(selected_clips_data: List[bytes]) -> None:
        for temp_file in selected_clips_data:
            os.remove(temp_file)

    async def __reply_clip_not_found(self, message: Message, clip_name: str, username: str) -> None:
        await message.answer(get_clip_not_found_message(clip_name))
        await self._log_system_message(logging.INFO, f"Clip '{clip_name}' not found for user '{username}'.")

    async def __reply_no_matching_clips_found(self, message: Message) -> None:
        await message.answer(get_no_matching_clips_found_message())
        await self._log_system_message(logging.INFO, "No matching clips found for compilation.")
