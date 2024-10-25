import pytest

from bot.tests.base_test import BaseTest


class TestListCommand(BaseTest):

    @pytest.mark.quick
    def test_list_after_search(self):
        search_command = '/szukaj krowa'
        search_expected_fragments = ["Znaleziono"]
        response_search = self.send_command(search_command)
        self.assert_response_contains(response_search, search_expected_fragments)

        list_command = '/lista'
        response_list = self.send_command(list_command)
        self.assert_file_matches(response_list, 'expected_list.txt', '.txt')
