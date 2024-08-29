import json
import logging
import os
import tempfile
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union, Any, Coroutine,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    EpisodeInfo,
    LastClip,
    SegmentInfo,
    ClipType,
)
from bot.handlers.bot_message_handler import BotMessageHandler
from bot.responses.not_sending_videos.save_clip_handler_responses import (
    get_clip_limit_exceeded_message,
    get_clip_name_exists_message,
    get_clip_name_length_exceeded_message,
    get_clip_name_not_provided_message,
    get_clip_saved_successfully_message,
    get_log_clip_name_exists_message,
    get_log_clip_saved_successfully_message,
    get_log_no_segment_selected_message,
    get_no_segment_selected_message,
)
from bot.settings import settings
from bot.video.clips_extractor import ClipsExtractor
from bot.video.utils import get_video_duration


class SaveClipHandler(BotMessageHandler):

    def get_commands(self) -> List[str]:
        return ["zapisz", "save", "z"]

    async def _do_handle(self, message: Message) -> None:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
            return
        clip_name = " ".join(content[1:])

        if len(clip_name) > settings.MAX_CLIP_NAME_LENGTH:
            await message.answer(get_clip_name_length_exceeded_message())
            return

        if not clip_name:
            return await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
        if not await DatabaseManager.is_clip_name_unique(message.chat.id, clip_name):
            return await self.__reply_clip_name_exists(message, clip_name)

        if (
                not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and
                await DatabaseManager.get_user_clip_count(message.chat.id) >= settings.MAX_CLIPS_PER_USER
        ):
            await message.answer(get_clip_limit_exceeded_message())
            return

        last_clip = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
        segment_dict = json.loads(last_clip.segment)
        if not last_clip:
            return await self.__reply_no_segment_selected(message)
        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip(last_clip)
        if not last_clip.clip_type == ClipType.COMPILED:
            await ClipsExtractor.extract_clip(segment_dict.get("video_path"), start_time, end_time, output_filename, self._logger)

        with open(output_filename, "rb") as f:
            video_data = f.read()

        duration = await get_video_duration(output_filename)

        await DatabaseManager.save_clip(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            clip_name=clip_name,
            video_data=video_data,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            is_compilation=is_compilation,
            season=season,
            episode_number=episode_number,
        )

        await self.__reply_clip_saved_successfully(message, clip_name)

    async def __prepare_clip(self, last_clip: LastClip):  #fixme to do type hinting:
        segment_dict = json.loads(last_clip.segment)
        episode_info = segment_dict.get("episode_info", {})
        season = episode_info.get("season")
        episode_number = episode_info.get("episode_number")

        with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4") as tmp_file:
            output_filename = tmp_file.name

        if last_clip.clip_type == ClipType.COMPILED:
            print("jestem w compiled")
            output_filename = self.__bytes_to_filepath(last_clip.compiled_clip)  # wyciągneicie z bytes i zapisanie do pliku
            is_compilation = True
            return output_filename.replace(" ", "_"), 0.0, 0.0, is_compilation, None, None

        if last_clip.clip_type == ClipType.ADJUSTED:
            print("jestem w adjusted")
            print(segment_dict.get("video_path"))
            print(segment_dict.get("start"))
            print(segment_dict.get("end"))
            print(segment_dict.get("season"))
            print(segment_dict.get("episode"))
            print(output_filename)
            print("------------------")
            print(last_clip)
            await ClipsExtractor.extract_clip(segment_dict.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time,
                                              output_filename, self._logger)
            return output_filename, last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

        if last_clip.clip_type == ClipType.SELECTED or last_clip.clip_type == ClipType.SINGLE or last_clip.clip_type == ClipType.MANUAL:
            print("jestem w selected, single, manual")
            await ClipsExtractor.extract_clip(segment_dict.get("video_path"), segment_dict.get("start"), segment_dict.get("end"), output_filename,
                                              self._logger)
            return output_filename.replace(" ", "_"), segment_dict.get("start"), segment_dict.get("end"), False, season, episode_number

    @staticmethod
    def __bytes_to_filepath(clip_data: bytes) -> str:
        with tempfile.NamedTemporaryFile(
                delete=False, delete_on_close=False, suffix=".mp4",
        ) as tmp_file:
            output_filename = tmp_file.name
        with open(output_filename, "wb") as f:
            f.write(clip_data)
        return output_filename

    async def __reply_clip_name_exists(self, message: Message, clip_name: str) -> None:
        await message.answer(get_clip_name_exists_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_name_exists_message(clip_name, message.from_user.username),
        )

    async def __reply_no_segment_selected(self, message: Message) -> None:
        await message.answer(get_no_segment_selected_message())
        await self._log_system_message(
            logging.INFO,
            get_log_no_segment_selected_message(),
        )

    async def __reply_clip_saved_successfully(self, message: Message, clip_name: str) -> None:
        await message.answer(get_clip_saved_successfully_message(clip_name))
        await self._log_system_message(
            logging.INFO,
            get_log_clip_saved_successfully_message(clip_name, message.from_user.username),
        )
