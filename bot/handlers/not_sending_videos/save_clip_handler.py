import json
import logging
import tempfile
from typing import (
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.models import (
    ClipType,
    LastClip,
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
        if await self.is_any_validation_failed(message):
            return

        clip_name = " ".join(message.text.split()[1:])
        last_clip = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
        output_filename, start_time, end_time, is_compilation, season, episode_number = await self.__prepare_clip(
            last_clip,
        )

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

    async def __prepare_clip(self, last_clip: LastClip) -> Tuple[str, float, float, bool, Optional[int], Optional[int]]:
        segment_dict: Dict[str, any] = json.loads(last_clip.segment)
        episode_info: Dict[str, Optional[int]] = segment_dict.get("episode_info", {})
        season: Optional[int] = episode_info.get("season")
        episode_number: Optional[int] = episode_info.get("episode_number")

        with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4") as tmp_file:
            output_filename: str = tmp_file.name

        clip_handlers: Dict[
            ClipType, Callable[[], Awaitable[Tuple[str, float, float, bool, Optional[int], Optional[int]]]],
        ] = {
            ClipType.COMPILED: lambda: self.__handle_compiled_clip(last_clip),
            ClipType.ADJUSTED: lambda: self.__handle_adjusted_clip(
                last_clip, segment_dict, output_filename, season,
                episode_number,
            ),
            ClipType.MANUAL: lambda: self.__handle_manual_clip(
                segment_dict, output_filename, season,
                episode_number,
            ),
            ClipType.SELECTED: lambda: self.__handle_selected_clip(
                last_clip, segment_dict, output_filename, season,
                episode_number,
            ),
            ClipType.SINGLE: lambda: self.__handle_single_clip(
                last_clip, segment_dict, output_filename, season,
                episode_number,
            ),
        }

        if last_clip.clip_type in clip_handlers:
            return await clip_handlers[last_clip.clip_type]()
        raise ValueError(f"Unsupported clip type: {last_clip.clip_type}")
    async def __handle_compiled_clip(self, last_clip: LastClip) -> Tuple[str, float, float, bool, None, None]:
        output_filename: str = self.__bytes_to_filepath(last_clip.compiled_clip)
        return output_filename.replace(" ", "_"), 0.0, 0.0, True, None, None

    async def __handle_adjusted_clip(
        self, last_clip: LastClip, segment_dict: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_dict.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time,
            output_filename, self._logger,
        )
        return output_filename, last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

    async def __handle_manual_clip(
        self, segment_dict: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_dict.get("video_path"), segment_dict.get("start"), segment_dict.get("end"), output_filename,
            self._logger,
        )
        return output_filename.replace(" ", "_"), segment_dict.get("start"), segment_dict.get(
            "end",
        ), False, season, episode_number

    async def __handle_selected_clip(
        self, last_clip: LastClip, segment_dict: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_dict.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time, output_filename,
            self._logger,
        )
        return output_filename.replace(
            " ",
            "_",
        ), last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

    async def __handle_single_clip(
        self, last_clip: LastClip, segment_dict: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_dict.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time, output_filename,
            self._logger,
        )
        return output_filename.replace(
            " ",
            "_",
        ), last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

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

    async def is_any_validation_failed(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
            return True

        clip_name = " ".join(content[1:])

        if len(clip_name) > settings.MAX_CLIP_NAME_LENGTH:
            await message.answer(get_clip_name_length_exceeded_message())
            return True

        if not clip_name:
            await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
            return True

        if not await DatabaseManager.is_clip_name_unique(message.chat.id, clip_name):
            await self.__reply_clip_name_exists(message, clip_name)
            return True

        if (
                not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and
                await DatabaseManager.get_user_clip_count(message.chat.id) >= settings.MAX_CLIPS_PER_USER
        ):
            await message.answer(get_clip_limit_exceeded_message())
            return True

        last_clip = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
        if not last_clip:
            await self.__reply_no_segment_selected(message)
            return True

        return False
