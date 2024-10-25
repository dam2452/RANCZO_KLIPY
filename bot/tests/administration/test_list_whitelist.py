import pytest

from bot.tests.base_test import BaseTest


class TestListWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_list_whitelist_with_users(self):
        response = self.send_command('/listwhitelist')
        expected_fragments = ["Lista użytkowników w Whitelist:"]
        self.assert_response_contains(response, expected_fragments)
