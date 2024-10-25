import pytest

from bot.tests.base_test import BaseTest


class TestListKeysCommand(BaseTest):

    @pytest.mark.quick
    def test_list_keys_with_keys(self):
        response = self.send_command('/listkey')
        expected_fragments = ["Lista kluczy subskrypcji"]
        self.assert_response_contains(response, expected_fragments)
