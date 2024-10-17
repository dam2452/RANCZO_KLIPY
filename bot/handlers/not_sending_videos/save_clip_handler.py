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
    ClipInfo,
    ClipPreparationResult,
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

    def _get_validator_functions(self) -> List[Callable[[Message], Awaitable[bool]]]:
        return [
            self._validate_clip_name_provided,
            self._validate_clip_name_length,
            self._validate_clip_name_unique,
            self._validate_clip_limit_not_exceeded,
            self._validate_last_clip_exists,
        ]

    async def _validate_clip_name_provided(self, message: Message) -> bool:
        content = message.text.split()
        if len(content) < 2:
            await self._reply_invalid_args_count(message, get_clip_name_not_provided_message())
            return False
        return True
    @staticmethod
    async def _validate_clip_name_length(message: Message) -> bool:
        clip_name = " ".join(message.text.split()[1:])
        if len(clip_name) > settings.MAX_CLIP_NAME_LENGTH:
            await message.answer(get_clip_name_length_exceeded_message())
            return False
        return True

    async def _validate_clip_name_unique(self, message: Message) -> bool:
        clip_name = " ".join(message.text.split()[1:])
        if not await DatabaseManager.is_clip_name_unique(message.chat.id, clip_name):
            await self.__reply_clip_name_exists(message, clip_name)
            return False
        return True

    @staticmethod
    async def _validate_clip_limit_not_exceeded(message: Message) -> bool:
        if (
            not await DatabaseManager.is_admin_or_moderator(message.from_user.id) and
            await DatabaseManager.get_user_clip_count(message.chat.id) >= settings.MAX_CLIPS_PER_USER
        ):
            await message.answer(get_clip_limit_exceeded_message())
            return False
        return True

    async def _validate_last_clip_exists(self, message: Message) -> bool:
        last_clip = await DatabaseManager.get_last_clip_by_chat_id(message.chat.id)
        if not last_clip:
            await self.__reply_no_segment_selected(message)
            return False
        return True
    async def _do_handle(self, message: Message) -> None:
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

    async def __prepare_clip(self, last_clip: LastClip) -> ClipPreparationResult:
        segment_json: Dict[str, any] = json.loads(last_clip.segment)
        episode_info: Dict[str, Optional[int]] = segment_json.get("episode_info", {})
        season: Optional[int] = episode_info.get("season")
        episode_number: Optional[int] = episode_info.get("episode_number")

        with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False, suffix=".mp4") as tmp_file:
            output_filename: str = tmp_file.name

        clip_handlers: Dict[
            ClipType, Callable[[], Awaitable[ClipPreparationResult]],
        ] = {
            ClipType.COMPILED: lambda: self.__handle_compiled_clip(last_clip),
            ClipType.ADJUSTED: lambda: self.__handle_adjusted_clip(
                last_clip, segment_json, output_filename, season,
                episode_number,
            ),
            ClipType.MANUAL: lambda: self.__handle_manual_clip(
                segment_json, output_filename, season,
                episode_number,
            ),
            ClipType.SELECTED: lambda: self.__handle_selected_clip(
                last_clip, segment_json, output_filename, season,
                episode_number,
            ),
            ClipType.SINGLE: lambda: self.__handle_single_clip(
                last_clip, segment_json, output_filename, season,
                episode_number,
            ),
        }

        if last_clip.clip_type in clip_handlers:
            return await clip_handlers[last_clip.clip_type]()
        raise ValueError(f"Unsupported clip type: {last_clip.clip_type}")

    async def __handle_compiled_clip(self, last_clip: LastClip) -> ClipPreparationResult:
        output_filename: str = self.__bytes_to_filepath(last_clip.compiled_clip)
        return ClipPreparationResult(
            output_filename=output_filename.replace(" ", "_"),
            start_time=0.0,
            end_time=0.0,
            is_compilation=True,
            season=None,
            episode_number=None,
        )

    async def __handle_adjusted_clip(
        self, last_clip: LastClip, segment_json: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_json.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time,
            output_filename, self._logger,
        )
        return output_filename, last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

    async def __handle_manual_clip(
        self, segment_json: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_json.get("video_path"), segment_json.get("start"), segment_json.get("end"), output_filename,
            self._logger,
        )
        return output_filename.replace(" ", "_"), segment_json.get("start"), segment_json.get(
            "end",
        ), False, season, episode_number

    async def __handle_selected_clip(
        self, last_clip: LastClip, segment_json: Dict[str, any], output_filename: str,
        season: Optional[int], episode_number: Optional[int],
    ) -> Tuple[
        str, float, float, bool, Optional[int], Optional[int],
    ]:
        await ClipsExtractor.extract_clip(
            segment_json.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time, output_filename,
            self._logger,
        )
        return output_filename.replace(
            " ",
            "_",
        ), last_clip.adjusted_start_time, last_clip.adjusted_end_time, False, season, episode_number

    async def __handle_single_clip(
            self, last_clip: LastClip, segment_json: Dict[str, any], output_filename: str,
            season: Optional[int], episode_number: Optional[int],
    ) -> ClipInfo:
        await ClipsExtractor.extract_clip(
            segment_json.get("video_path"), last_clip.adjusted_start_time, last_clip.adjusted_end_time, output_filename,
            self._logger,
        )
        return ClipInfo(
            output_filename=output_filename.replace(" ", "_"),
            start_time=last_clip.adjusted_start_time,
            end_time=last_clip.adjusted_end_time,
            is_compilation=False,
            season=season,
            episode_number=episode_number,
        )
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
