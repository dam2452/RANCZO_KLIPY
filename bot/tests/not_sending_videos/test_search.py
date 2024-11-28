import pytest

import bot.responses.not_sending_videos.search_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSearchCommand(BaseTest):

    @pytest.mark.quick
    def test_search_existing_word(self):
        self.expect_command_result_contains('/szukaj krowa', ["Znaleziono"])

    @pytest.mark.quick
    def test_search_nonexistent_word(self):
        self.expect_command_result_contains(
            '/szukaj nieistniejące_słowo',
            [msg.get_invalid_args_count_message()],
        )

    @pytest.mark.long
    def test_search_existing_word_short_command(self):
        self.expect_command_result_contains('/sz krowa', ["Znaleziono"])

    @pytest.mark.long
    def test_search_nonexistent_word_short_command(self):
        self.expect_command_result_contains(
            '/sz nieistniejące_słowo',
            [msg.get_invalid_args_count_message()],
        )
