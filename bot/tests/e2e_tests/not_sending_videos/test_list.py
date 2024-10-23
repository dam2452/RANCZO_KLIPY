import logging
import os

from bot.tests.e2e_tests.base_e2e_test import BaseE2ETest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestListCommand(BaseE2ETest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    def test_list_after_search(self):
        response_search = self.send_command('/szukaj krowa')
        expected_text = "Znaleziono"
        assert expected_text in response_search.text, f'Oczekiwany tekst "{expected_text}" nie został znaleziony w odpowiedzi "{response_search.text}".'

        response_list = self.send_command('/lista')

        assert response_list.media is not None, 'Bot nie odesłał żadnego pliku.'
        assert response_list.file.ext == '.txt', 'Bot nie odesłał pliku .txt.'

        received_file_path = self.client.download_media(response_list, file='received_list.txt')

        expected_file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                'expected_files',
                'expected_list.txt',
            ),
        )

        assert os.path.exists(expected_file_path), f'Oczekiwany plik {expected_file_path} nie istnieje.'

        expected_hash = self.compute_file_hash(expected_file_path)
        received_hash = self.compute_file_hash(received_file_path)

        assert expected_hash == received_hash, 'Otrzymany plik różni się od oczekiwanego.'

        # noinspection PyTypeChecker
        os.remove(received_file_path)
