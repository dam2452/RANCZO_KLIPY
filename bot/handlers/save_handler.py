import logging
import os
import tempfile
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager
from bot.utils.global_dicts import (
    last_compiled_clip,
    last_manual_clip,
    last_selected_segment,
)
from bot.utils.video_handler import VideoProcessor


class SaveClipHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['zapisz', 'save', 'z']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/zapisz {message.text}")
        username = message.from_user.username
        chat_id = message.chat.id
        content = message.text.split()
        if len(content) < 2:
            return await self.__reply_no_clip_name_provided(message)

        clip_name = content[1]

        if not await DatabaseManager.is_clip_name_unique(chat_id, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)

        # fixme: moze jakas funkcja ktora nazywa ten warunek bo troche slabo?
        if chat_id not in last_selected_segment and chat_id not in last_compiled_clip and chat_id not in last_manual_clip:
            return await self.__reply_no_segment_selected(message)

        # fixme: krzywe to jakies xD moze tez to jakos nazwac i w funkcje?
        segment_info = last_selected_segment.get(chat_id) or last_compiled_clip.get(chat_id) or last_manual_clip.get(
            chat_id,
        )

        if 'episode_info' in segment_info:
            await self._log_system_message(logging.INFO, f"Segment Info: {segment_info['episode_info']}")
        else:
            await self._log_system_message(logging.INFO, "Segment Info: Compiled or manual clip without episode info")

        # fixme tyle najebane to moze jakas klasa/dataclass?
        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip_file(
            segment_info,
        )

        actual_duration = await VideoProcessor.get_video_duration(output_filename)
        if actual_duration is None:
            await self.__reply_failed_to_verify_clip_length(message, clip_name)
            os.remove(output_filename)
            return

        end_time = start_time + int(actual_duration)

        with open(output_filename, 'rb') as file:
            video_data = file.read()

        os.remove(output_filename)

        # fixme: (data)class Clip?
        await DatabaseManager.save_clip(
            chat_id=chat_id,
            username=username,
            clip_name=clip_name,
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
            is_compilation=is_compilation,
            season=season,
            episode_number=episode_number,
        )

        await self.__reply_clip_saved_successfully(message, clip_name)

    @staticmethod
    async def __prepare_clip_file(segment_info):  # fixme jakies zjebane to jest XD i z powtórkami ale na razie chuj, type hint?
        start_time = 0
        end_time = 0
        is_compilation = False
        season = None
        episode_number = None

        if 'compiled_clip' in segment_info:
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(output_filename, 'wb') as f:
                compiled_clip = segment_info['compiled_clip']
                if isinstance(compiled_clip, bytes):
                    f.write(compiled_clip)
                else:
                    f.write(compiled_clip.getvalue())
            is_compilation = True
        elif 'expanded_clip' in segment_info:
            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(output_filename, 'wb') as f:
                expanded_clip = segment_info['expanded_clip']
                if isinstance(expanded_clip, bytes):
                    f.write(expanded_clip)
                else:
                    f.write(expanded_clip.getvalue())
            start_time = segment_info.get('expanded_start', 0)
            end_time = segment_info.get('expanded_end', 0)
            season = segment_info.get('episode_info', {}).get('season')
            episode_number = segment_info.get('episode_info', {}).get('episode_number')
        else:
            segment = segment_info
            clip_path = segment['video_path']
            start_time = segment['start']
            end_time = segment['end']
            is_compilation = False
            season = segment['episode_info']['season']
            episode_number = segment['episode_info']['episode_number']

            output_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            await VideoProcessor.extract_clip(clip_path, start_time, end_time, output_filename)

        return output_filename, start_time, end_time, is_compilation, season, episode_number

    async def __reply_no_clip_name_provided(self, message: Message) -> None:
        await message.answer("📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu")
        await self._log_system_message(logging.INFO, "No clip name provided by user.")

    async def __reply_clip_name_exists(self, message: Message, clip_name: str) -> None:
        await message.answer("⚠️ Klip o takiej nazwie już istnieje. Wybierz inną nazwę.⚠️")
        await self._log_system_message(
            logging.INFO,
            f"Clip name '{clip_name}' already exists for user '{message.from_user.username}'.",
        )

    async def __reply_no_segment_selected(self, message: Message) -> None:
        await message.answer("⚠️ Najpierw wybierz segment za pomocą /klip, /wytnij lub skompiluj klipy.⚠️")
        await self._log_system_message(
            logging.INFO,
            "No segment selected, manual clip, or compiled clip available for user.",
        )

    async def __reply_failed_to_verify_clip_length(self, message: Message, clip_name: str) -> None:
        await message.answer("❌ Nie udało się zweryfikować długości klipu.❌")
        await self._log_system_message(
            logging.ERROR,
            f"Failed to verify the length of the clip '{clip_name}' for user '{message.from_user.username}'.",
        )

    async def __reply_clip_saved_successfully(self, message: Message, clip_name: str) -> None:
        await message.answer(f"✅ Klip '{clip_name}' został zapisany pomyślnie. ✅")
        await self._log_system_message(logging.INFO, f"Clip '{clip_name}' saved successfully for user '{message.from_user.username}'.")
