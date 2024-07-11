import json
import logging
import os
import tempfile
from typing import (
    Dict,
    List,
)

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    Message,
)
from bot_message_handler import BotMessageHandler

from bot.utils.database import DatabaseManager
from bot.utils.video_handler import VideoManager

last_compiled_clip: Dict[int, json] = {}


async def compile_clips(selected_clips_data: List[bytes], bot: Bot) -> str:  # fixme to chyba też jakiś wylot do utils
    temp_files = []
    for video_data in selected_clips_data:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_files.append(temp_file.name)
        with open(temp_file.name, 'wb') as f:
            f.write(video_data)

    compiled_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    compiled_output.close()

    await VideoManager(bot).concatenate_clips(temp_files, compiled_output.name)

    file_size_mb = os.path.getsize(compiled_output.name) / (1024 * 1024)
    if file_size_mb > 50:  # Fixme: jakis util function typu assert_valid_file_size ktory robi dokladnie to, zeby nie hardkodowac tych 50 syfiasto
        raise ValueError(f"Compiled clip exceeds size limit: {file_size_mb:.2f} MB")

    return compiled_output.name


async def send_compiled_clip(chat_id: int, compiled_output: str, bot: Bot) -> None:
    with open(compiled_output, 'rb') as f:
        compiled_clip_data = f.read()

    last_compiled_clip[chat_id] = {
        'compiled_clip': compiled_clip_data,
        'is_compilation': True,
    }

    await bot.send_video(chat_id, FSInputFile(compiled_output), supports_streaming=True, width=1920, height=1080)


async def clean_up_temp_files(compiled_output: str, selected_clips_data) -> None:
    for temp_file in selected_clips_data:
        os.remove(temp_file)
    os.remove(compiled_output)


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
            await clean_up_temp_files(compiled_output, selected_clips_data)

            await self._log_system_message(
                logging.INFO,
                f"Compiled clip sent to user '{username}' and temporary files removed.",
            )
        except Exception as e:
            await self.__reply_compilation_error(message, e)

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
