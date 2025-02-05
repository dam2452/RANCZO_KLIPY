import asyncio
import hashlib
import json
import logging
from pathlib import Path
import re
import secrets
import time
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

import pytest
from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message

from bot.database.database_manager import DatabaseManager
from bot.responses.bot_message_handler_responses import get_response
from bot.search.transcription_finder import TranscriptionFinder
import bot.tests.messages as msg
from bot.tests.settings import settings as s

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BaseTest:
    client: TelegramClient
    @pytest.fixture(autouse=True)
    def setup_client(self, telegram_client) -> None:
        self.client = telegram_client
    @staticmethod
    def __sanitize_text(text: str) -> str:
        text = text.replace('\xa0', ' ')
        sanitized = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        sanitized = " ".join(sanitized.split())
        return sanitized.lower()

    def get_tested_handler_name(self) -> str:
        return self.__class__.__name__[4:]

    async def get_response(self, key: str, args: Optional[List[str]] = None) -> str:
        return await get_response(
            key=key,
            handler_name=self.get_tested_handler_name() ,
            args=args,
        )

    @staticmethod
    def remove_until_first_space(text: str) -> str:
        return text.split(' ', 1)[-1] if ' ' in text else text

    async def send_command(self, command_text: str, timeout: int = 10, poll_interval: float = 0.5) -> Message:
        sent_message = await self.client.send_message(s.BOT_USERNAME, command_text)
        sent_message_id = sent_message.id

        start_time = time.time()

        while time.time() - start_time < timeout:
            async for message in self.client.iter_messages(
                    s.BOT_USERNAME,
                    min_id=sent_message_id,
                    reverse=True,
            ):
                if not message.out and message.id > sent_message_id:
                    logger.info(f"Bot response: {message.text}")
                    return message

            await asyncio.sleep(poll_interval)

        raise TimeoutError(msg.bot_response_timeout())

    def assert_response_contains(self, response: Message, expected_fragments: List[str]) -> bool:
        error_message = msg.missing_fragment("{fragment}", "{response}")
        return self.__check_response_fragments(expected_fragments, response, error_message)

    async def assert_command_result_file_matches(
            self,
            response: Message,
            expected_filename: str,
            expected_extension: Optional[str] = None,
            received_filename: str = 'received_file',
    ) -> None:
        assert response.media is not None, msg.file_not_returned()

        if expected_extension:
            assert response.file.ext == expected_extension, msg.file_extension_mismatch(
                expected_extension,
                response.file.ext,
            )

        received_file_path = Path(
            str(await self.client.download_media(response, file=f'{received_filename}{expected_extension or ""}')),
        )
        expected_hashes_path = Path(__file__).parent / 'expected_file_hashes.json'

        assert expected_hashes_path.exists(), msg.hash_file_not_found()

        with open(expected_hashes_path, 'r', encoding= 'UTF-8') as f:
            expected_hashes = json.load(f)

        assert expected_filename in expected_hashes, msg.hash_not_found(expected_filename)

        expected_hash = expected_hashes[expected_filename]

        received_hash = self.__compute_file_hash(received_file_path)

        assert expected_hash == received_hash, msg.file_mismatch()

        received_file_path.unlink()
        logger.info(msg.file_test_success(expected_filename))

    @staticmethod
    def remove_n_lines(text: str, n: int) -> str:
        lines = text.splitlines()
        return "\n".join(lines[n:])

    async def expect_command_result_contains(self, command: str, expected: List[str]) -> None:
        self.assert_response_contains(await self.send_command(command, timeout=60), expected)

    @staticmethod
    def __compute_file_hash(file_path: Path, hash_function: str = 'sha256') -> str:
        hash_func = hashlib.new(hash_function)
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def __check_response_fragments(expected_fragments: List[str], response: Message, error_message: str) -> bool:
        sanitized_response = BaseTest.__sanitize_text(response.text)

        for fragment in expected_fragments:
            sanitized_fragment = BaseTest.__sanitize_text(fragment)
            if sanitized_fragment not in sanitized_response:
                raise AssertionError(error_message.format(fragment=fragment, response=response.text))
        return True
    @staticmethod
    def generate_random_username(length: int = 8) -> str:
        return f"user_{secrets.token_hex(length // 2)}"


    async def add_test_user(
        self,
            user_id: Optional[int] = None,
            username: Optional[str] = None,
            full_name: str = "Test User",
            note: Optional[str] = None,
            subscription_days: Optional[int] = None,
    ) -> Dict[str, Union[int, str]]:
        user_id = user_id or secrets.randbits(32)
        username = username or self.generate_random_username()

        await DatabaseManager.add_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
            note=note,
            subscription_days=subscription_days,
        )

        return {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "note": note,
            "subscription_days": subscription_days,
        }
    @staticmethod
    async def add_test_admin_user() -> Dict[str, Union[int, str]]:
        await DatabaseManager.add_user(
            user_id=s.DEFAULT_ADMIN,
            username=s.ADMIN_USERNAME,
            full_name=s.ADMIN_FULL_NAME,
            note=None,
            subscription_days=None,
        )
        return {
            "user_id": s.DEFAULT_ADMIN,
            "username": s.ADMIN_USERNAME,
            "full_name": s.ADMIN_FULL_NAME,
        }
    @staticmethod
    async def switch_to_normal_user() -> None:
        await DatabaseManager.remove_admin(s.DEFAULT_ADMIN)
        await DatabaseManager.add_subscription(s.DEFAULT_ADMIN, 2137)

    @staticmethod
    async def switch_to_admin_user() -> None:
        await DatabaseManager.add_admin(s.DEFAULT_ADMIN)
        await DatabaseManager.remove_subscription(s.DEFAULT_ADMIN)

    @staticmethod
    async def calculate_hash_of_message(message: str) -> str:
        return hashlib.sha256(message.encode()).hexdigest()

    async def assert_message_hash_matches(
            self,
            message: Message,
            expected_key: str,
            expected_hashes_file: str = 'expected_file_hashes.json',
    ) -> None:
        sanitized_message = self.__sanitize_text(message.text)

        computed_hash = hashlib.sha256(sanitized_message.encode()).hexdigest()

        expected_hashes_path = Path(__file__).parent / expected_hashes_file
        assert expected_hashes_path.exists(), "Expected hashes file not found!"

        with open(expected_hashes_path, 'r', encoding='UTF-8') as f:
            expected_hashes = json.load(f)

        assert expected_key in expected_hashes, f"Expected key '{expected_key}' not found in hashes file!"

        expected_hash = expected_hashes[expected_key]

        assert computed_hash == expected_hash, (
            f"Hash mismatch for key '{expected_key}': "
            f"expected {expected_hash}, got {computed_hash}"
        )

        logger.info(f"Message hash test passed for key: {expected_key}")

    @staticmethod
    def remove_first_line(text: str) -> str:
        return "\n".join(text.splitlines()[1:])

    async def expect_command_result_hash(
        self,
        command: str,
        expected_key: str,
        expected_hashes_file: str = 'expected_file_hashes.json',
        timeout: int = 10,
    ) -> None:

        response = await self.send_command(command, timeout=timeout)
        await self.assert_message_hash_matches(
            response,
            expected_key=expected_key,
            expected_hashes_file=expected_hashes_file,
        )

    @staticmethod
    async def get_season_info() -> Dict[str, int]:
        season_info = await TranscriptionFinder.get_season_details_from_elastic(
            logger=logger,
        )
        return season_info
