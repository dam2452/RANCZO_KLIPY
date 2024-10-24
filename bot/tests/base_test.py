import hashlib
import logging
import os
import time
from typing import (
    Dict,
    List,
    Optional,
)

from telethon.sync import TelegramClient
from telethon.tl.custom.message import Message

from bot.tests.settings import settings as s

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseTest:
    client: Optional[TelegramClient] = None
    logger = logger

    @classmethod
    def setup_class(cls) -> None:
        if s.SESSION:
            cls.client = TelegramClient(s.SESSION, s.API_ID, s.API_HASH)
            cls.logger.info('Klient Telegram został utworzony z sesją.')
        else:
            cls.client = TelegramClient('test_session', s.API_ID, s.API_HASH)
        cls.client.start(password=s.PASSWORD, phone=s.PHONE)
        cls.logger.info('Klient Telegram został uruchomiony.')

    @classmethod
    def teardown_class(cls) -> None:
        cls.client.disconnect()
        cls.logger.info('Klient Telegram został rozłączony.')

    def send_command(self, command_text: str) -> Message:
        sent_message = self.client.send_message(s.BOT_USERNAME, command_text)
        # noinspection PyUnresolvedReferences
        sent_message_id = sent_message.id

        time.sleep(5)

        messages = self.client.iter_messages(
            s.BOT_USERNAME,
            min_id=sent_message_id,
            reverse=True,
        )

        for message in messages:
            if message.out:
                continue
            if message.id <= sent_message_id:
                continue
            self.logger.info(f'Odpowiedź bota: {message.text}')
            return message
        raise ValueError("Bot nie odpowiedział na komendę.")

    @staticmethod
    def compute_file_hash(file_path, hash_function='sha256'):
        hash_func = hashlib.new(hash_function)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def check_response_fragments(expected_fragments: List[str], response: Message, error_message: str):
        for fragment in expected_fragments:
            if fragment not in response.text:
                raise AssertionError(error_message.format(fragment=fragment, response=response.text))
        return True

    def assert_response_contains(self, response: Message, expected_fragments: List[str]):
        error_message = 'Oczekiwany fragment "{fragment}" nie został znaleziony w odpowiedzi "{response}".'
        return self.check_response_fragments(expected_fragments, response, error_message)

    def run_test_cases(self, test_cases: List[Dict[str, List[str]]]):
        for case in test_cases:
            commands = case['command']
            expected_fragments = case['expected_fragments']

            for command in commands:
                response = self.send_command(command)
                self.assert_response_contains(response, expected_fragments)

            self.logger.info(f"Test komend {commands} zakończony sukcesem.")

    def assert_video_matches(self, response: Message, expected_video_filename: str, received_video_filename: str = 'received_video.mp4'):
        assert response.media is not None, 'Bot nie zwrócił wideo.'

        received_video_path = self.client.download_media(response, file=received_video_filename)

        expected_video_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'expected_videos',
                expected_video_filename,
            ),
        )

        assert os.path.exists(expected_video_path), f'Oczekiwane wideo {expected_video_path} nie istnieje.'

        expected_hash = self.compute_file_hash(expected_video_path)
        received_hash = self.compute_file_hash(received_video_path)

        assert expected_hash == received_hash, 'Otrzymane wideo różni się od oczekiwanego.'

        os.remove(str(received_video_path))
        self.logger.info(f"Test wideo {expected_video_filename} zakończony sukcesem.")

    def assert_file_matches(self, response: Message, expected_file_filename: str, expected_extension: str, received_file_filename: str = 'received_file'):
        assert response.media is not None, 'Bot nie zwrócił pliku.'

        assert response.file.ext == expected_extension, (f'Bot zwrócił plik z nieprawidłowym rozszerzeniem. '
                                                         f'Oczekiwano {expected_extension}, otrzymano {response.file.ext}.')

        received_file_path = self.client.download_media(response, file=f'{received_file_filename}{expected_extension}')

        expected_file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'expected_files',
                expected_file_filename,
            ),
        )

        assert os.path.exists(expected_file_path), f'Oczekiwany plik {expected_file_path} nie istnieje.'

        expected_hash = self.compute_file_hash(expected_file_path)
        received_hash = self.compute_file_hash(received_file_path)

        assert expected_hash == received_hash, 'Otrzymany plik różni się od oczekiwanego.'

        os.remove(str(received_file_path))
        self.logger.info(f"Test pliku {expected_file_filename} zakończony sukcesem.")
