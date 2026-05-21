import json
from pathlib import Path
import re
import shutil
from typing import (
    List,
    Optional,
)

from bot.adapters.signal.signal_http_client import SignalHttpClient
from bot.exceptions.video_exceptions import VideoTooLargeException
from bot.interfaces.responder import AbstractResponder


class SignalResponder(AbstractResponder):
    _MAX_MESSAGE_LENGTH = 2000

    __MD_UNESCAPE = re.compile(r'\\([*_`\[\]()~>#+=|{}.!\-])')

    def __init__(self, client: SignalHttpClient, recipient: str) -> None:
        self.__client = client
        self.__recipient = recipient

    @staticmethod
    def __unescape_markdown_v2(text: str) -> str:
        return SignalResponder.__MD_UNESCAPE.sub(r'\1', text)

    @staticmethod
    def __strip_markdown(text: str) -> str:
        text = SignalResponder.__MD_UNESCAPE.sub(r'\1', text)
        return re.sub(r'[*_`~]', '', text)

    async def _send_text_part(self, text: str, reply_to_id: Optional[int] = None) -> Optional[int]:
        await self.__client.send_text(self.__recipient, self.__strip_markdown(text))
        return None

    async def _send_markdown_part(self, text: str, reply_to_id: Optional[int] = None) -> Optional[int]:
        await self.__client.send_text(
            self.__recipient, self.__unescape_markdown_v2(text), styled=True,
        )
        return None

    async def send_photo(self, image_bytes: bytes, image_path: Path, caption: Optional[str] = None) -> None:
        suffix = image_path.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        await self.__client.send_attachment(
            self.__recipient, image_bytes, image_path.name, mime,
            self.__unescape_markdown_v2(caption) if caption else "",
        )

    async def send_video(
        self,
        file_path: Path,
        delete_after_send: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[float] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 95:
                raise VideoTooLargeException(duration=duration, suggestions=suggestions)
            await self.__client.send_file(self.__recipient, str(file_path))
        finally:
            if delete_after_send:
                file_path.unlink(missing_ok=True)

    async def send_document(
        self,
        file_path: Path,
        caption: str,
        delete_after_send: bool = True,
        cleanup_dir: Optional[Path] = None,
    ) -> None:
        try:
            await self.__client.send_file(
                self.__recipient, str(file_path), self.__unescape_markdown_v2(caption),
            )
        finally:
            if cleanup_dir:
                shutil.rmtree(cleanup_dir, ignore_errors=True)
            elif delete_after_send:
                file_path.unlink(missing_ok=True)

    async def send_json(self, data: json) -> None:
        raise NotImplementedError("JSON mode not supported for SignalResponder")
