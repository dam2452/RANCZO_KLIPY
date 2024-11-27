import pytest

from bot.tests.base_test import BaseTest


class TestListCommand(BaseTest):

    @pytest.mark.quick
    def test_list_after_search(self):
        self.expect_command_result_contains('/szukaj krowa', ["Znaleziono"])
        response_list = self.send_command('/lista')
        self.assert_file_matches(response_list, 'expected_list.txt', '.txt')
