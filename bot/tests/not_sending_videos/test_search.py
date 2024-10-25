import pytest

from bot.tests.base_test import BaseTest


class TestSearchCommand(BaseTest):

    @pytest.mark.quick
    def test_search_existing_word(self):
        response = self.send_command('/szukaj krowa')
        expected_fragments = ["Znaleziono"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.quick
    def test_search_nonexistent_word(self):
        response = self.send_command('/szukaj nieistniejące_słowo')
        expected_fragments = ["❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_search_existing_word_short_command(self):
        response = self.send_command('/sz krowa')
        expected_fragments = ["Znaleziono"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_search_nonexistent_word_short_command(self):
        response = self.send_command('/sz nieistniejące_słowo')
        expected_fragments = ["❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌"]
        self.assert_response_contains(response, expected_fragments)
