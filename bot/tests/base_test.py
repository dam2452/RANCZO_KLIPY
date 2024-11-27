import hashlib
import logging
from pathlib import Path
import time
from typing import (
    List,
    Optional,
)

from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message

import bot.tests.messages as msg
from bot.tests.settings import settings as s

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BaseTest:
    client: Optional[TelegramClient] = None
    logger = logger

    @classmethod
    def setup_class(cls) -> None:
        if s.SESSION:
            cls.client = TelegramClient(s.SESSION, s.API_ID, s.API_HASH)
            cls.logger.info(msg.client_created())
        else:
            cls.client = TelegramClient('test_session', s.API_ID, s.API_HASH)
        cls.client.start(password=s.PASSWORD, phone=s.PHONE)
        cls.logger.info(msg.client_started())

    @classmethod
    def teardown_class(cls) -> None:
        cls.client.disconnect()
        cls.logger.info(msg.client_disconnected())

    def send_command(self, command_text: str, timeout: int = 10, poll_interval: float = 0.5) -> Message:
        sent_message = self.client.send_message(s.BOT_USERNAME, command_text)
        # noinspection PyUnresolvedReferences
        sent_message_id = sent_message.id

        start_time = time.time()

        while time.time() - start_time < timeout:
            messages = self.client.iter_messages(
                s.BOT_USERNAME,
                min_id=sent_message_id,
                reverse=True,
            )

            for message in messages:
                if message.out:
                    continue
                if message.id > sent_message_id:
                    self.logger.info(f"Bot response: {message.text}")
                    return message

            time.sleep(poll_interval)

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
        self.logger.info(msg.video_test_success(expected_video_filename))

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
        self.logger.info(msg.file_test_success(expected_file_filename))

    def expect_command_result_contains(self, command: str, expected: List[str]) -> None:
        self.assert_response_contains(self.send_command(command), expected)

    @staticmethod
    def __compute_file_hash(file_path: Path, hash_function: str = 'sha256'):
        hash_func = hashlib.new(hash_function)
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def __check_response_fragments(expected_fragments: List[str], response: Message, error_message: str):
        for fragment in expected_fragments:
            if fragment not in response.text:
                raise AssertionError(error_message.format(fragment=fragment, response=response.text))
        return True
