import logging

from bot.tests.e2e_tests.base_e2e_test import BaseE2ETest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSearchHandler(BaseE2ETest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    def test_search_geniusz(self):
        response = self.send_command('/szukaj geniusz')
        expected_text = "Znaleziono"
        assert expected_text in response.text, f'Oczekiwany tekst "{expected_text}" nie został znaleziony w odpowiedzi "{response.text}".'

    def test_search_no_results(self):
        non_existent_quote = 'nieistniejące_słowo'
        response = self.send_command(f'/szukaj {non_existent_quote}')
        expected_text = f"❌ Nie znaleziono pasujących cytatów dla: '{non_existent_quote}'.❌"
        assert expected_text in response.text, f'Oczekiwany tekst "{expected_text}" nie został znaleziony w odpowiedzi "{response.text}".'

def main():
    test = TestSearchHandler()
    test.setup_class()
    test.test_search_geniusz()
    test.test_search_no_results()
    test.teardown_class()

if __name__ == '__main__':
    main()
