import logging

from bot.tests.e2e_tests.base_e2e_test import BaseE2ETest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStartCommand(BaseE2ETest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    def test_start(self):
        response = self.send_command('/start')

        expected_fragments = [
            "Podstawowe komendy",
        ]

        for fragment in expected_fragments:
            assert fragment in response.text, f'Oczekiwany fragment "{fragment}" nie został znaleziony w odpowiedzi "{response.text}".'

        logger.info("Test komendy /start zakończony sukcesem.")
