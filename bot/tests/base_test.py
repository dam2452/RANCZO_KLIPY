import asyncio
import hashlib
import logging
from pathlib import Path
import re
import time
from typing import List

import pytest
from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message

import bot.tests.messages as msg
from bot.tests.settings import settings as s

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BaseTest:
    client: TelegramClient
    @pytest.fixture(autouse=True)
    def setup_client(self, telegram_client):
        self.client = telegram_client
    @staticmethod
    def __sanitize_text(text: str) -> str:
        sanitized = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        sanitized = " ".join(sanitized.split())
        return sanitized.lower()
    async def send_command(self, command_text: str, timeout: int = 10, poll_interval: float = 0.5):
        sent_message = await self.client.send_message(s.BOT_USERNAME, command_text)
        sent_message_id = sent_message.id

        start_time = time.time()

        while time.time() - start_time < timeout:
            async for message in self.client.iter_messages(
                    s.BOT_USERNAME,
                    min_id=sent_message_id,
                    reverse=True,
            ):
                if message.out:
                    continue
                if message.id > sent_message_id:
                    logger.info(f"Bot response: {message.text}")
                    return message

            await asyncio.sleep(poll_interval)

        raise TimeoutError(msg.bot_response_timeout())

    def assert_response_contains(self, response: Message, expected_fragments: List[str]):
        error_message = msg.missing_fragment("{fragment}", "{response}")
        return self.__check_response_fragments(expected_fragments, response, error_message)

    def assert_video_matches(self, response: Message, expected_video_filename: str, received_video_filename: str = 'received_video.mp4'):
        assert response.media is not None, msg.video_not_returned()


        received_video_path = Path(str(self.client.download_media(response, file=received_video_filename)))

        expected_video_path = Path(__file__).parent / 'expected' / 'expected_videos' / expected_video_filename

        assert expected_video_path.exists(), msg.video_not_found(expected_video_filename)

        expected_hash = self.__compute_file_hash(expected_video_path)
        received_hash = self.__compute_file_hash(received_video_path)

        assert expected_hash == received_hash, msg.video_mismatch()

        received_video_path.unlink()
        logger.info(msg.video_test_success(expected_video_filename))

    def assert_file_matches(self, response: Message, expected_file_filename: str, expected_extension: str, received_file_filename: str = 'received_file'):
        assert response.media is not None, msg.file_not_returned()

        assert response.file.ext == expected_extension, msg.file_extension_mismatch(expected_extension, response.file.ext)

        received_file_path = Path(str(self.client.download_media(response, file=f'{received_file_filename}{expected_extension}')))

        expected_file_path = Path(__file__).parent / 'expected' / 'expected_files' / expected_file_filename

        assert expected_file_path.exists(), msg.file_not_found(expected_file_filename)

        expected_hash = self.__compute_file_hash(expected_file_path)
        received_hash = self.__compute_file_hash(received_file_path)

        assert expected_hash == received_hash, msg.file_mismatch()

        received_file_path.unlink()
        logger.info(msg.file_test_success(expected_file_filename))

    async def expect_command_result_contains(self, command: str, expected: List[str]) -> None:
        self.assert_response_contains(await self.send_command(command), expected)

    @staticmethod
    def __compute_file_hash(file_path: Path, hash_function: str = 'sha256'):
        hash_func = hashlib.new(hash_function)
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def __check_response_fragments(expected_fragments: List[str], response: Message, error_message: str):
        sanitized_response = BaseTest.__sanitize_text(response.text)

        for fragment in expected_fragments:
            sanitized_fragment = BaseTest.__sanitize_text(fragment)
            if sanitized_fragment not in sanitized_response:
                raise AssertionError(error_message.format(fragment=fragment, response=response.text))
        return True
