import pytest

from bot.tests.base_test import BaseTest


class TestSearchCommand(BaseTest):

    @pytest.mark.quick
    def test_search_existing_word(self):
        self.expect_command_result_contains('/szukaj krowa', ["Znaleziono"])

    @pytest.mark.quick
    def test_search_nonexistent_word(self):
        self.expect_command_result_contains(
            '/szukaj nieistniejące_słowo',
            ["❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌"]
        )

    @pytest.mark.long
    def test_search_existing_word_short_command(self):
        self.expect_command_result_contains('/sz krowa', ["Znaleziono"])

    @pytest.mark.long
    def test_search_nonexistent_word_short_command(self):
        self.expect_command_result_contains(
            '/sz nieistniejące_słowo',
            ["❌ Nie znaleziono pasujących cytatów dla: 'nieistniejące_słowo'.❌"]
        )
