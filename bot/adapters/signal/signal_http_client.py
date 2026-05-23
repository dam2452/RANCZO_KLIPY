import asyncio
import base64
import json
import logging
import mimetypes
from pathlib import Path
from typing import (
    Awaitable,
    Callable,
    Dict,
    Optional,
    Set,
)

import aiohttp

logger = logging.getLogger(__name__)

_WS_RECONNECT_DELAY = 5
_ATTACHMENT_LIMIT_MB = 95


class SignalHttpClient:
    def __init__(self, base_url: str, phone: str) -> None:
        self.__base_url = base_url.rstrip("/")
        self.__phone = phone
        self.__session: Optional[aiohttp.ClientSession] = None
        self.__receive_task: Optional[asyncio.Task] = None
        self.__pending: Set[asyncio.Task] = set()

    async def start(self) -> None:
        self.__session = aiohttp.ClientSession()

    async def stop(self) -> None:
        if self.__receive_task:
            self.__receive_task.cancel()
            try:
                await self.__receive_task
            except asyncio.CancelledError:
                pass
        if self.__session:
            await self.__session.close()

    def start_receiving(self, handler: Callable[[Dict], Awaitable[None]]) -> None:
        if self.__receive_task is not None:
            raise RuntimeError("SignalHttpClient is already receiving")
        self.__receive_task = asyncio.create_task(self.__receive_loop(handler))

    async def send_text(
        self,
        recipient: str,
        text: str,
        styled: bool = False,
        quote_timestamp: Optional[int] = None,
        quote_author: Optional[str] = None,
    ) -> None:
        body: Dict = {
            "message": text,
            "number": self.__phone,
            "recipients": [recipient],
        }
        if styled:
            body["text_mode"] = "styled"
        if quote_timestamp is not None and quote_author is not None:
            body["quote_timestamp"] = quote_timestamp
            body["quote_author"] = quote_author
        await self.__post("/v2/send", body)

    async def send_attachment(
        self,
        recipient: str,
        data: bytes,
        filename: str,
        mime_type: str,
        caption: str = "",
    ) -> None:
        encoded = base64.b64encode(data).decode()
        attachment = f"data:{mime_type};filename={filename};base64,{encoded}"
        await self.__post(
            "/v2/send", {
                "message": caption,
                "number": self.__phone,
                "recipients": [recipient],
                "base64_attachments": [attachment],
                "text_mode": "styled",
            },
        )

    async def send_file(
        self,
        recipient: str,
        file_path: str,
        caption: str = "",
    ) -> None:
        path = Path(file_path)
        data = await asyncio.to_thread(path.read_bytes)
        file_size_mb = len(data) / (1024 * 1024)
        if file_size_mb > _ATTACHMENT_LIMIT_MB:
            raise RuntimeError(
                f"File too large for Signal: {file_size_mb:.1f}MB "
                f"(limit: {_ATTACHMENT_LIMIT_MB}MB)",
            )
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        await self.send_attachment(recipient, data, path.name, mime_type, caption)

    async def send_reaction(
        self,
        recipient: str,
        emoji: str,
        target_author: str,
        timestamp: int,
    ) -> None:
        await self.__post(
            f"/v1/reactions/{self.__phone}", {
                "reaction": emoji,
                "recipient": recipient,
                "target_author": target_author,
                "timestamp": timestamp,
            },
        )

    async def delete_reaction(
        self,
        recipient: str,
        target_author: str,
        timestamp: int,
    ) -> None:
        await self.__delete(
            f"/v1/reactions/{self.__phone}", {
                "recipient": recipient,
                "target_author": target_author,
                "timestamp": timestamp,
            },
        )

    async def send_read_receipt(
        self,
        recipient: str,
        timestamp: int,
        receipt_type: str = "read",
    ) -> None:
        await self.__post(
            f"/v1/receipts/{self.__phone}", {
                "receipt_type": receipt_type,
                "recipient": recipient,
                "timestamp": timestamp,
            },
        )

    async def set_typing(self, recipient: str, typing: bool = True) -> None:
        url = f"/v1/typing-indicator/{self.__phone}"
        body: Dict = {"recipient": recipient}
        if typing:
            await self.__put(url, body)
        else:
            await self.__delete(url, body)

    async def download_attachment(self, attachment_id: str) -> bytes:
        session = await self.__ensure_session()
        async with session.get(
            f"{self.__base_url}/v1/attachments/{attachment_id}",
        ) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def __ensure_session(self) -> aiohttp.ClientSession:
        if self.__session is None:
            raise RuntimeError("SignalHttpClient has not been started")
        return self.__session

    async def __post(self, path: str, body: Dict) -> None:
        session = await self.__ensure_session()
        async with session.post(f"{self.__base_url}{path}", json=body) as resp:
            await self.__check_response(path, resp)

    async def __put(self, path: str, body: Dict) -> None:
        session = await self.__ensure_session()
        async with session.put(f"{self.__base_url}{path}", json=body) as resp:
            await self.__check_response(path, resp)

    async def __delete(self, path: str, body: Dict) -> None:
        session = await self.__ensure_session()
        async with session.delete(f"{self.__base_url}{path}", json=body) as resp:
            await self.__check_response(path, resp)

    @staticmethod
    async def __check_response(path: str, resp: aiohttp.ClientResponse) -> None:
        if resp.status >= 400:
            text = await resp.text()
            logger.error("Signal API %d on %s: %s", resp.status, path, text[:500])
        resp.raise_for_status()

    async def __receive_loop(self, handler: Callable[[Dict], Awaitable[None]]) -> None:
        ws_url = f"{self.__base_url}/v1/receive/{self.__phone}"
        logger.info("Signal WebSocket receiving started: %s", ws_url)

        while True:
            try:
                session = await self.__ensure_session()
                async with session.ws_connect(ws_url) as ws:
                    logger.info("Signal WebSocket connected.")
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            task = asyncio.create_task(handler(json.loads(msg.data)))
                            self.__pending.add(task)
                            task.add_done_callback(self.__pending.discard)
                        elif msg.type in (
                            aiohttp.WSMsgType.ERROR,
                            aiohttp.WSMsgType.CLOSED,
                        ):
                            break

                logger.warning("Signal WebSocket closed. Reconnecting in %ds...", _WS_RECONNECT_DELAY)
            except Exception as exc:
                logger.warning("Signal WebSocket error: %s. Reconnecting in %ds...", exc, _WS_RECONNECT_DELAY)

            await asyncio.sleep(_WS_RECONNECT_DELAY)
