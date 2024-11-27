import pytest

import bot.responses.administration.list_whitelist_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestListWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_list_whitelist_with_users(self):
        self.expect_command_result_contains(
            '/listwhitelist',
            [msg.create_whitelist_response([])],  # Replace with a mock list of users for testing
        )
